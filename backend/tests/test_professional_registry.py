"""Synthetic registry responses; lookup must NEVER authenticate the applicant."""
import httpx
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize('mode,expected,status', [
    ('active','record_found',200), ('inactive','inactive',200),
    ('organization','organization',200), ('empty','not_found',200),
    ('failure',None,503), ('malformed',None,503), ('oversized',None,503),
])
async def test_registry_is_read_only_and_fails_closed(client, monkeypatch, mode, expected, status):
    from app.auth import registry
    real_client = httpx.AsyncClient
    def respond(request):
        assert request.url.host == 'npiregistry.cms.hhs.gov'
        assert dict(request.url.params) == {'version':'2.1', 'number':'1234567893'}
        if mode == 'failure': return httpx.Response(503)
        if mode == 'malformed': return httpx.Response(200,json=[])
        if mode == 'oversized': return httpx.Response(200,content=b'x'*70000)
        record = {'number':'1234567893', 'enumeration_type':'NPI-2' if mode == 'organization' else 'NPI-1',
            'basic': {'first_name':'SYNTHETIC','last_name':'PROVIDER', 'status':'D' if mode == 'inactive' else 'A'},
            'taxonomies':[{'primary':True,'desc':'Synthetic specialty'}],
            'addresses':[{'telephone_number':'DO NOT RETURN'}]}
        return httpx.Response(200,json={'results':[] if mode == 'empty' else [record]})
    monkeypatch.setattr(registry.httpx, 'AsyncClient', lambda **kw: real_client(transport=httpx.MockTransport(respond), **kw))
    result = await client.post('/api/v1/credentials/npi',json={'npi':'1234567893'})
    assert result.status_code == status
    if expected:
        body = result.json()
        assert body['status'] == expected
        assert body['identity_verified'] is body['license_verified'] is body['access_granted'] is False
        assert 'DO NOT RETURN' not in result.text
    assert (await client.get('/api/v1/inbox')).status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize('number', ['1234567890','9999999999','abc','123', 'https://evil.test'])
async def test_invalid_registry_numbers_are_rejected(client, number):
    assert (await client.post('/api/v1/credentials/npi',json={'npi':number})).status_code == 422
