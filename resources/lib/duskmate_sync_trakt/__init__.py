__all__ = ('Provider',)


def __getattr__(name):
    """Load the full sync provider only when a consumer requests it.

    Standalone script actions such as Duskmate token provisioning do not run inside TMDb
    Helper's module environment and must be able to import their small submodules independently.
    """
    if name == 'Provider':
        from duskmate_sync_trakt.provider import Provider
        return Provider
    raise AttributeError(name)
