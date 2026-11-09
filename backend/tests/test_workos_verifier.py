"""Real RSA signature checks with a local test key; no provider accounts or network."""
import time
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from fastapi import HTTPException
import jwt
from jwt.algorithms import RSAAlgorithm
from app.auth import workos_verifier as verifier
from app.models.schemas import UserRole


@pytest.fixture
def signed(monkeypatch):
    private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    public = private.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    key = RSAAlgorithm.to_jwk(private.public_key(), as_dict=True)
    key['kid'] = 'test-key'
    monkeypatch.setattr(verifier.settings, 'workos_client_id', 'client_test')
    monkeypatch.setattr(verifier.settings, 'workos_organization_id', 'org_test')
    monkeypatch.setattr(verifier, '_keys', {'test-key': key})
    monkeypatch.setattr(verifier, '_expires', time.monotonic() + 300)
    monkeypatch.setattr(verifier, '_client_id', 'client_test')
    def token(**changes):
        claims = dict(sub='user_test', sid='session_test', client_id='client_test', org_id='org_test',
                      iss='https://api.workos.com', iat=int(time.time()), exp=int(time.time()) + 120,
                      permissions=['omnimatch:access'])
        claims.update(changes)
        return jwt.encode(claims, pem, algorithm='RS256', headers={'kid': 'test-key'})
    return token


@pytest.mark.asyncio
async def test_staff_and_admin(signed):
    assert (await verifier.verify_workos_token(signed())).role == UserRole.CLINICAL_STAFF
    assert (await verifier.verify_workos_token(signed(permissions=['omnimatch:access', 'omnimatch:admin']))).role == UserRole.ADMIN


@pytest.mark.asyncio
@pytest.mark.parametrize('changes,status', [
    ({'exp': 1}, 401), ({'client_id': 'client_other'}, 401), ({'iss': 'https://example.com'}, 401),
    ({'sid': None}, 401), ({'org_id': 'org_other'}, 403), ({'permissions': []}, 403),
    ({'permissions': ['omnimatch:admin']}, 403), ({'permissions': 'omnimatch:access'}, 403),
    ({'iat': int(time.time()) + 3600}, 401), ({'sub': ''}, 401), ({'sid': ''}, 401),
])
async def test_reject_claims(signed, changes, status):
    with pytest.raises(HTTPException) as error:
        await verifier.verify_workos_token(signed(**changes))
    assert error.value.status_code == status


@pytest.mark.asyncio
async def test_tampered_signature(signed):
    token = signed()
    header, payload, signature = token.split('.')
    signature = ('A' if signature[0] != 'A' else 'B') + signature[1:]
    with pytest.raises(HTTPException) as error:
        await verifier.verify_workos_token('.'.join([header, payload, signature]))
    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_no_symmetric_fallback(signed):
    token = jwt.encode({'sub': 'fake'}, 'test-secret-for-rejected-hs256-signature'*2, algorithm='HS256', headers={'kid': 'test-key'})
    with pytest.raises(HTTPException) as error:
        await verifier.verify_workos_token(token)
    assert error.value.status_code == 401


@pytest.mark.asyncio
async def test_blank_configuration_fails_closed(signed, monkeypatch):
    monkeypatch.setattr(verifier.settings, 'workos_client_id', '')
    with pytest.raises(HTTPException) as error:
        await verifier.verify_workos_token(signed())
    assert error.value.status_code == 503


@pytest.mark.asyncio
async def test_provider_failure_fails_closed(signed, monkeypatch):
    import httpx
    monkeypatch.setattr(verifier, '_expires', 0)
    async def unavailable(*args, **kwargs):
        raise httpx.ConnectError('test outage')
    monkeypatch.setattr(httpx.AsyncClient, 'get', unavailable)
    with pytest.raises(HTTPException) as error:
        await verifier.verify_workos_token(signed())
    assert error.value.status_code == 503
