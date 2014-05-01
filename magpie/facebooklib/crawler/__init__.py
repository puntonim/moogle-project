from requests_oauthlib import OAuth2Session

from utils.db import session_autocommit
from .response import FacebookResponse


class FacebookCrawler:
    """
    Web crawler to query Facebook and collect posts for a `bearertoken`.

    Parameters:
    bearertoken -- a `models.BearerToken`
    """
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    @property
    def _client(self):
        """
        A `OAuth1Session` for the current `bearertoken`.
        It is a cached attribute so that it is a singleton.
        """
        try:
            cl = self._client_cached
        except AttributeError:
            cl = self._client_cached = OAuth2Session(
                client_id=self.bearertoken.provider.client_id,
                token=self.bearertoken.token_set
            )
        return cl

    def run(self):
        """
        Crawl Facebook for new posts and write en entry for each item to Redis.
        """
        is_first_loop = True  # for pagination
        next = ''  # for pagination
        while True:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                self.bearertoken = sex.merge(self.bearertoken)

                resource_url = self.build_resource_url(next)

                # Query Twitter.
                # Note: the correctness of the response is checked when creating
                # TwitterResponse(r).
                r = self._client.get(resource_url)

                # Parse the response.
                response = FacebookResponse(r)
                response.parse(self.bearertoken.id)

                # Pagination
                if is_first_loop:
                    updates_cursor = response.updates_cursor
                    is_first_loop = False

                # Continue only in case Facebook `has_more` items to send.
                if response.has_more:
                    next = response.next
                    continue
                break

        # Update the updates_cursor only at the end, when everything has been successfully
        # completed
        self._update_updates_cursor(updates_cursor)

    def build_resource_url(self, next):
        """
        Build the URL to use to query Facebook.
        The URL is build such as it manages the pagination.

        Parameters:
        next -- the next parameter got from Facebook when the response has more pages.
        """
        # Fields filter
        # TODO I might want to add more fields like comments or likes, but bare in mind that
        # TODO when doing so, you want to use: .limit(x)
        # TODO https://developers.facebook.com/docs/graph-api/using-graph-api/
        fields = 'fields=id,message,updated_time'

        # The cursor
        since = self.build_since_parameter()

        if next:
            return '{}&{}'.format(next, since)
        return 'https://graph.facebook.com/v2.0/me/statuses?{}&{}'.format(fields, since)

    def build_since_parameter(self):
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

    def _update_updates_cursor(self, new_updates_cursor):
        """
        Update the updates_cursor parameter on the database.
        """
        if new_updates_cursor:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                bearertoken = sex.merge(self.bearertoken)

                bearertoken.updates_cursor = new_updates_cursor