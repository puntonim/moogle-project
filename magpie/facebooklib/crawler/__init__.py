import logging
from requests_oauthlib import OAuth2Session

from .response import ApiFacebookResponse
from crawler import AbstractCrawler


log = logging.getLogger('facebook')


class FacebookCrawler(AbstractCrawler):
    """
    Web crawler to query Facebook and collect posts for a `bearertoken`.

    Parameters:
    bearertoken -- a `models.BearerToken`
    """
    def _init_client(self):
        return OAuth2Session(
            client_id=self.bearertoken.provider.client_id,
            token=self.bearertoken.token_set
        )

    @staticmethod
    def _init_response(*args, **kwargs):
        return ApiFacebookResponse(*args, **kwargs)

    def _build_resource_url(self, pagination_cursor):
        """
        Build the URL to use to query Facebook.
        The URL is build such as it manages the pagination.

        Parameters:
        pagination_cursor -- the `next` parameter got from Facebook when the response
        has more pages.
        """
        # Fields filter
        # TODO I might want to add more fields like comments or likes, but bare in mind that
        # TODO when doing so, you want to use: .limit(x)
        # TODO https://developers.facebook.com/docs/graph-api/using-graph-api/
        fields = 'fields=id,from,type,created_time,updated_time,message'

        # The cursor
        since = self._build_since_parameter()

        url = 'https://graph.facebook.com/v2.0/me/feed?{}&{}'.format(fields, since)
        if pagination_cursor:
            url = '{}&{}'.format(pagination_cursor, since)

        log.debug("Querying URL:\n{}".format(url))
        return url

    def _build_since_parameter(self):
        """
        Build the since parameter used for pagination as explained here:
        https://developers.facebook.com/docs/graph-api/using-graph-api/#paging
        """
        try:  # check whether _updates_cursor has already been initialized
            cur = self._updates_cursor
        except AttributeError:
            cur = self._updates_cursor = self.bearertoken.updates_cursor

        if cur:
            return 'since={}'.format(cur)
        return ''