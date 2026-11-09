"""Fail closed on obvious public-deployment misconfiguration."""
from urllib.parse import urlsplit


def validate_production(settings):
    if settings.app_env != 'production':
        return
    if not settings.encrypted_storage_confirmed:
        raise RuntimeError('Production requires independently verified encrypted storage.')
    origins = settings.allowed_origins_list
    if not origins or any(urlsplit(origin).scheme != 'https' or not urlsplit(origin).hostname or urlsplit(origin).path not in ('', '/') for origin in origins):
        raise RuntimeError('Production requires explicit HTTPS browser origins.')
    if not settings.workos_client_id or not settings.workos_organization_id:
        raise RuntimeError('Production requires configured owner-approved account access.')
    if settings.app_secret_key == settings.jwt_secret_key or any(len(value) < 32 or 'change' in value.lower() for value in [settings.app_secret_key, settings.jwt_secret_key]):
        raise RuntimeError('Production requires independent random application secrets.')
