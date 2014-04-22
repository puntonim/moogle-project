from requests_oauthlib import OAuth1Session

from utils.db import session_autocommit
from .response import TwitterResponse


class TwitterCrawler:
    """
    Web crawler to query Twitter and collect tweets for a `bearertoken`.
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
            cl = self._client_cached = OAuth1Session(
                client_key=self.bearertoken.provider.client_id,
                client_secret=self.bearertoken.provider.client_secret,
                resource_owner_key=self.bearertoken.oauth_token,
                resource_owner_secret=self.bearertoken.oauth_token_secret
            )
        return cl

    def run(self):
        """
        Crawl Twitter for new tweets and write en entry for each item to Redis.
        """
        is_first_loop = True  # for pagination
        max_id = ''  # for pagination
        while True:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                self.bearertoken = sex.merge(self.bearertoken)

                resource_url = self.build_resource_url(max_id)

                # Query Twitter.
                r = self._client.get(resource_url)
                # TODO
                print('{}\n>>>>>>>>>>>>>{}'.format(resource_url, r.status_code))

                # Parse the response.
                response = TwitterResponse(r)
                response.parse(self.bearertoken.id)

                # Pagination
                if is_first_loop:
                    updates_cursor = response.updates_cursor
                    is_first_loop = False
                max_id = response.max_id

                # Continue only in case Twitter `has_more` items to send.
                if response.has_more:
                    continue
                break

        # Update the updates_cursor only at the end, when everything has been successfully
        # completed
        self._update_updates_cursor(updates_cursor)

    def build_resource_url(self, max_id):
        """
        Build the URL to use to query Twitter.
        The URL is build such as it manages the pagination.

        Parameters:
        max_id -- the parameter used for pagination as explained here:
        https://dev.twitter.com/docs/working-with-timelines
        """
        return ('https://api.twitter.com/1.1/statuses/user_timeline.json?' +
                'trim_user=true&' +
                'count=25&' +  # Number of tweets returned
                'user_id={}&'.format(self.bearertoken.user_id) +
                #'user_id=6253282&'  # +  # TODO @twitterapi
                '{}&'.format(self.build_since_id_parameter()) +
                '{}'.format(self.build_max_id_parameter(max_id))
        )

    def build_since_id_parameter(self):
        """
        Build the since_id parameter used for pagination as explained here:
        https://dev.twitter.com/docs/working-with-timelines
        """
        try:  # check whether _updates_cursor has already been initialized
            cur = self._updates_cursor
        except AttributeError:
            cur = self._updates_cursor = self.bearertoken.updates_cursor

        if cur:
            return 'since_id={}'.format(cur)
        return ''

    @staticmethod
    def build_max_id_parameter(max_id):
        """
        Build the max_id parameter for pagination as explained here:
        https://dev.twitter.com/docs/working-with-timelines
        """
        if max_id:
            return 'max_id={}'.format(max_id)
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