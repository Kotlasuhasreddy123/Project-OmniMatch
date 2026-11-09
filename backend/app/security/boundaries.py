"""Deterministic HTTP and compute boundaries; no clinical text is logged here."""
import asyncio
from urllib.parse import urlsplit
from fastapi import HTTPException
from starlette.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from app.config import settings

JSON_LIMIT = 512 * 1024
AUDIO_LIMIT = 50 * 1024 * 1024
_inference_lock = asyncio.Lock()


async def bounded_inference(function):
    # One worker is required for this in-process admission control.
    if _inference_lock.locked():
        raise HTTPException(429, 'Another model task is running. Please retry shortly.', headers={'Retry-After': '5'})
    async with _inference_lock:
        return await run_in_threadpool(function)


class RequestBoundaryMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        headers = dict(scope['headers'])
        async def reject(code, message):
            await JSONResponse({'detail': message}, status_code=code)(scope, receive, send)
        host = headers.get(b'host', b'').decode('latin1')
        try:
            hostname = urlsplit('//'+host).hostname or ''
        except ValueError:
            return await reject(400, 'Invalid request host.')
        if hostname.lower() not in settings.allowed_hosts_list:
            return await reject(400, 'Request host is not allowed.')
        origin = headers.get(b'origin', b'').decode('latin1')
        if scope['method'] in {'POST', 'PUT', 'PATCH', 'DELETE'} and origin and origin not in settings.allowed_origins_list:
            return await reject(403, 'This website origin is not allowed.')
        lengths = [value for key, value in scope['headers'] if key == b'content-length']
        limit = AUDIO_LIMIT if scope['path'] == '/api/v1/audio/transcribe' else JSON_LIMIT
        if lengths:
            if len(lengths) != 1 or not lengths[0].isdigit():
                return await reject(400, 'Invalid request length.')
            if int(lengths[0]) > limit:
                return await reject(413, 'Request is too large.')
        if limit == JSON_LIMIT:
            body = bytearray()
            deadline = asyncio.get_running_loop().time() + 15
            while True:
                try:
                    message = await asyncio.wait_for(receive(), max(.001, deadline - asyncio.get_running_loop().time()))
                except asyncio.TimeoutError:
                    return await reject(408, 'Request upload timed out.')
                if message['type'] == 'http.disconnect':
                    return
                body.extend(message.get('body', b''))
                if len(body) > limit:
                    return await reject(413, 'Request is too large.')
                if not message.get('more_body', False):
                    break
            delivered = False
            async def replay_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {'type': 'http.request', 'body': bytes(body), 'more_body': False}
                return await receive()
            return await self.app(scope, replay_receive, send)
        size = 0
        deadline = asyncio.get_running_loop().time() + 60
        async def bounded_receive():
            nonlocal size
            try:
                message = await asyncio.wait_for(receive(), max(.001, deadline - asyncio.get_running_loop().time()))
            except asyncio.TimeoutError:
                raise HTTPException(408, 'Request upload timed out.')
            if message['type'] == 'http.request':
                size += len(message.get('body', b''))
                if size > limit:
                    raise HTTPException(413, 'Request is too large.')
            return message
        await self.app(scope, bounded_receive, send)
