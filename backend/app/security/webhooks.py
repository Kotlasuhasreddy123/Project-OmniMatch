"""Opt-in, owner-configured destinations only. Never accept a caller URL."""
import asyncio
import ipaddress
import socket
from urllib.parse import urlsplit
import httpx
from app.config import settings


async def post_configured_webhook(url, payload):
    if not settings.outbound_webhooks_enabled:
        return False
    configured = {value for value in [settings.referral_webhook_url, settings.digest_webhook_url] if value}
    if not url or url not in configured:
        return False
    try:
        parsed = urlsplit(url)
        hosts = {host.strip().lower() for host in settings.webhook_allowed_hosts.split(',') if host.strip()}
        if (parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.port not in (None, 443)
                or parsed.username or parsed.password or parsed.fragment or len(url) > 2048):
            return False
        addresses = await asyncio.to_thread(socket.getaddrinfo, parsed.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):
            return False
        # Environment proxies and redirects cannot override the approved target.
        # The owner must use a trusted provider domain; an egress firewall is
        # still required to enforce destination IPs against DNS rebinding.
        async with httpx.AsyncClient(timeout=10, trust_env=False, follow_redirects=False) as client:
            response = await client.post(url, json=payload)
            return 200 <= response.status_code < 300
    except (ValueError, OSError, httpx.HTTPError):
        return False
