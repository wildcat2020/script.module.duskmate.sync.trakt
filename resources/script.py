import os
import sys
from xbmc import executebuiltin


# Kodi executes this file as a script, so the add-on's xbmc.python.module extension is not
# applied to the script itself. Add our library explicitly before importing provider modules.
LIBRARY_PATH = os.path.join(os.path.dirname(__file__), 'lib')
if LIBRARY_PATH not in sys.path:
    sys.path.insert(0, LIBRARY_PATH)


def run(action=None, payload=None, **parameters):
    if action is None:
        executebuiltin(
            'RunScript(plugin.video.duskmate,configure_sync_provider,'
            'addon_id=script.module.duskmate.sync.trakt)')
        return
    if action == 'provision':
        from duskmate_sync_trakt.provisioning import provision_authorization
        return provision_authorization(**parameters)
    from tmdbhelper_lib.sync.providers.interface import SyncProviderRegistry
    provider = SyncProviderRegistry().find_provider('trakt')
    if provider is None:
        return
    if action in ('authenticate', 'revoke'):
        from duskmate_sync_trakt.account import TraktAccountActions
        actions = TraktAccountActions(provider)
        return {'authenticate': actions.authenticate, 'revoke': actions.revoke}[action]()
    if payload is not None:
        from json import loads
        from urllib.parse import unquote
        parameters.update(loads(unquote(payload)))
    from duskmate_sync_trakt.diagnostics import run_diagnostic
    return run_diagnostic(provider, action, **parameters)


if __name__ == '__main__':
    run(**dict(arg.split('=', 1) for arg in sys.argv[1:]))
