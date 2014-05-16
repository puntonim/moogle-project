import logging
from requests_oauthlib import OAuth1Session

from .response import ApiTwitterResponse
from crawler import AbstractCrawler


log = logging.getLogger('twitter')


class TwitterCrawler(AbstractCrawler):
    """
    Web crawler to query Twitter and collect tweets for a `bearertoken`.

    Parameters:
    bearertoken -- a `models.BearerToken`
    """
    def _init_client(self):
        return OAuth1Session(
            client_key=self.bearertoken.provider.client_id,
            client_secret=self.bearertoken.provider.client_secret,
            resource_owner_key=self.bearertoken.oauth_token,
            resource_owner_secret=self.bearertoken.oauth_token_secret
        )

    @staticmethod
    def _init_response(*args, **kwargs):
        return ApiTwitterResponse(*args, **kwargs)

    def _build_resource_url(self, pagination_cursor):
        """
        Build the URL to use to query Twitter.
        The URL is build such as it manages the pagination.

        Parameters:
        max_id -- the `max_id` parameter got from Twitter and used for pagination as explained
        here: https://dev.twitter.com/docs/working-with-timelines
        """
        return ('https://api.twitter.com/1.1/statuses/user_timeline.json?' +
                'trim_user=true&' +
                'count=100&' +  # Number of tweets returned in each page.
                'user_id={}&'.format(self.bearertoken.user_id) +
                #'user_id=6253282&' +  # TODO DEBUG @twitterapi
                #'user_id=14885549&' +  # TODO DEBUG @ForbesTech
                #'user_id=7144422&' +  # TODO DEBUG @lifehacker
                #'user_id=20536157&' +  # TODO DEBUG @google
                '{}&'.format(self._build_since_id_parameter()) +
                '{}'.format(self._build_max_id_parameter(pagination_cursor))
        )

    def _build_since_id_parameter(self):
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
    def _build_max_id_parameter(max_id):
        """
        Build the max_id parameter for pagination as explained here:
        https://dev.twitter.com/docs/working-with-timelines
        """
        if max_id:
            return 'max_id={}'.format(max_id)
        return ''