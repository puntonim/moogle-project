import logging
import json

from utils.exceptions import TwitterResponseError
from ..entry import ApiTwitterEntry
from ..redislist import RedisTwitterList
from response import AbstractApiResponse


log = logging.getLogger('twitter')


class ApiTwitterResponse(AbstractApiResponse):
    """
    Response got after a query to Twitter.

    Parameters:
    response -- a `requests.models.Response` instance.
    """
    def _sanity_check(self):
        """
        Check whether the current response got from Twitter is an error response.
        """
        log.debug('Response got: {}\n{}'.format(self.response.status_code,
                                                json.dumps(self.response.json(), indent=4)))

        # If the HTTP status code is not 200, then it is an error.
        # https://dev.twitter.com/docs/error-codes-responses
        if self.response.status_code != 200:
            msg = 'HTTP Status: {}\n{}'.format(self.response.status_code, self.response.json())
            raise TwitterResponseError(msg)
        # TODO implement a check on rate limit error (max 180 GET requests per access_token
        # TODO every 15 min): https://dev.twitter.com/docs/rate-limiting/1.1/limits

    def _init_redis_list(self, *args, **kwargs):
        return RedisTwitterList(*args, **kwargs)

    def _hook_parse_first_entry(self, entry):
        self._build_updates_cursor(entry)
        # Has more: we suppose that if there is at least an entry in this response,
        # then the response is not complete and a new query should be run (this is
        # not exactly true, but it works since it stops when the response has no entry).
        self.has_more = True

    def _build_updates_cursor(self, entry):
        # Updates cursor: the `id` of the most recent post.
        self.updates_cursor = entry.id

    def _hook_parse_last_entry(self, entry):
        #if self.has_more:
        self._build_pagination_cursor(entry)

    def _build_pagination_cursor(self, entry):
        # Pagination cursor: `id` - 1 of the oldest post in this page.
        self.pagination_cursor = str(int(entry.id) - 1)

    def _init_api_provider_entry(self, *args, **kwargs):
        return ApiTwitterEntry(*args, **kwargs)