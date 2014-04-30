from requests_oauthlib import OAuth2Session

from utils.db import session_autocommit
#from .response import FacebookResponse


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
        next = ''  # for pagination
        while True:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                self.bearertoken = sex.merge(self.bearertoken)

                print("----- Client id =", self.bearertoken.provider.client_id)
                print("----- Access token =", self.bearertoken.access_token)

                resource_url = self.build_resource_url(next)

                # Query Twitter.
                # Note: the correctness of the response is checked when creating TwitterResponse(r).
                r = self._client.get(resource_url)

                import json
                print(json.dumps(r.json(), indent=4))

                break

    def build_resource_url(self, next):
        """
        Build the URL to use to query Facebook.
        The URL is build such as it manages the pagination.

        Parameters:
        next -- the next parameter got from Facebook when the response has more pages.
        """
        # Fields filter
        # TODO ci sono altri campi da aggiungere qui al filtro
        # TODO I might want to add more fields like comments or likes, but bare in mind that
        # TODO when doing so, you want to use: .limit(x)
        # TODO # https://developers.facebook.com/docs/graph-api/using-graph-api/
        fields = 'fields=id,message,updated_time'

        # The cursor
        since = self.build_since_parameter()

        if next:
            return '{}&{}'.format(next, since)
        return 'https://graph.facebook.com/me/statuses?{}&{}'.format(fields, since)

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