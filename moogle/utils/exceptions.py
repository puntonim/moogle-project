class ResponseError(Exception):
    """An error response was received from a HTTP request."""
    pass


class SolrResponseError(ResponseError):
    """An error response was received from Solr."""
    pass