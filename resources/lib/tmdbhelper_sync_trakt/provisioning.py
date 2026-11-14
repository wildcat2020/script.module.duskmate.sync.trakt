import time

from tmdbhelper.lib.files.futils import json_dumps
from tmdbhelper_sync_trakt.settings import TraktSettings


MINIMUM_LIFETIME = 60


def provision(access_token=None, expires_at=None, **kwargs):
    """Store an app-managed Trakt access token without duplicating its refresh token."""
    access_token = (access_token or '').strip()
    now = int(time.time())
    try:
        expires_at = int(expires_at)
    except (TypeError, ValueError):
        raise ValueError('A valid Trakt token expiry is required')
    if not access_token:
        raise ValueError('A Trakt access token is required')
    if expires_at - now < MINIMUM_LIFETIME:
        raise ValueError('The Trakt access token expires too soon')

    authorization = {
        'access_token': access_token,
        'created_at': now,
        'expires_in': expires_at - now,
        'managed_by': 'duskmate',
        'scope': 'public',
        'token_type': 'bearer',
    }
    settings = TraktSettings()
    settings.migrate_setting('token', json_dumps(authorization))
    settings.migrate_setting('credentials_migrated', 'true')
    settings.clear_authorization_session()
    return True
