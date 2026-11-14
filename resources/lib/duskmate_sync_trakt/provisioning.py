import json
import time
from base64 import urlsafe_b64decode
from binascii import Error as Base64Error

MINIMUM_LIFETIME = 60
ADDON_ID = 'script.module.duskmate.sync.trakt'


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
    # This route is deliberately standalone: Kodi executes the provider script outside TMDb
    # Helper's Python module environment. Persist through the provider's own Addon instance so
    # Kodi cannot later overwrite a cross-add-on settings cache.
    from xbmcaddon import Addon
    from xbmcgui import Window

    addon = Addon(ADDON_ID)
    stored = json.dumps(authorization, separators=(',', ':'), sort_keys=True)
    addon.setSetting('token', stored)
    addon.setSetting('credentials_migrated', 'true')
    if addon.getSetting('token') != stored:
        raise RuntimeError('Kodi did not retain the Duskmate Trakt authorization')
    window = Window(10000)
    for name in (
            'TraktUserToken', 'TraktIsAuth', 'TraktRefreshAttempts',
            'TraktRefreshTimeStamp', 'TraktAttemptedLogin'):
        window.clearProperty(name)
    return True
