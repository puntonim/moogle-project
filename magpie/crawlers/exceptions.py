class ImproperlyConfigured(Exception):
    """Magpie is somehow improperly configured"""
    pass

class InconsistentItemError(Exception):
    """One of the items are not consistent"""
    pass