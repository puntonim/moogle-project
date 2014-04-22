class ImproperlyConfigured(Exception):
    """Magpie is somehow improperly configured"""
    pass


class InconsistentItemError(Exception):
    """One of the items are not consistent"""
    pass


class EntryNotToBeIndexed(Exception):
    """A entry that should not be indexed like a dir in Dropbox"""
    pass


class RedisEntryInconsistentError(Exception):
    """An inconsistent `RedisEntry`"""
    pass

class TwitterResponseError(Exception):
    """An error response was received from Twitter"""
    pass