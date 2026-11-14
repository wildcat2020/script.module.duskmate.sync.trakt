import json
import time
from base64 import urlsafe_b64decode
from binascii import Error as Base64Error

from tmdbhelper.lib.files.futils import json_dumps
from duskmate_sync_trakt.settings import TraktSettings


MINIMUM_LIFETIME = 60


def provision_authorization(authorization=None, **kwargs):
    if not authorization:
        raise ValueError('A Trakt authorization payload is required')
    try:
        payload = json.loads(urlsafe_b64decode(f'{authorization}===').decode('utf-8'))
    except (Base64Error, TypeError, UnicodeDecodeError, ValueError) as error:
        raise ValueError('The Trakt authorization payload is invalid') from error
    return provision(
        access_token=payload.get('access_token'),
        expires_at=payload.get('expires_at'),
    )


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
