class ImproperlyConfigured(Exception):
    """Magpie is somehow improperly configured."""
    pass


class InconsistentItemError(Exception):
    """One of the items are not consistent."""
    pass


class EntryNotToBeIndexed(Exception):
    """A entry that should not be indexed like a dir in Dropbox."""
    pass


class ResponseError(Exception):
    """An error response was received from a HTTP request."""
    pass


class TwitterResponseError(ResponseError):
    """An error response was received from Twitter."""
    pass


class FacebookResponseError(ResponseError):
    """An error response was received from Twitter."""
    pass


class SolrResponseError(ResponseError):
    """An error response was received from Solr."""
    pass