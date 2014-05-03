import logging
import json

from utils.exceptions import TwitterResponseError
from ..entry import ApiTwitterEntry
from ..redis import RedisTwitterList


log = logging.getLogger('twitter')


class TwitterResponse:
    """

    Parameters:
    response -- a `requests.models.Response` instance.
    """

    def __init__(self, response):
        self.response = response
        self.updates_cursor = ''
        self.max_id = ''
        self.has_more = False

        log.debug('Response got:\n{}'.format(json.dumps(self.response.json(), indent=4)))
        self._sanity_check()

    def _sanity_check(self):
        """
        Check whether the current response got from Twitter is an error response.
        """
        # If the HTTP status code is not 200, then it is an error.
        # https://dev.twitter.com/docs/error-codes-responses
        if self.response.status_code != 200:
            msg = 'HTTP Status: {}\n{}'.format(self.response.status_code, self.response.json())
            raise TwitterResponseError(msg)
        # TODO implement a check on rate limit error (max 180 GET requests per access_token
        # TODO every 15 min): https://dev.twitter.com/docs/rate-limiting/1.1/limits

    def parse(self, bearertoken_id):
        redis = RedisTwitterList(bearertoken_id)

        is_first_entry = True  # for updates cursor
        for entry in self._entries_to_apitwitterentries():
            # `entry` is a `ApiTwitterEntry` instance.

            #print(entry.texts)
            redis.buffer(entry)

            # Pagination.
            # We suppose that if there is at least an entry in this response, then the response
            # is not complete and a new query should be run (this is not exactly true, but it
            # works since it stops when the response has no entry).
            if is_first_entry:
                self.has_more = True
                self.updates_cursor = entry.id_str
                is_first_entry = False
            self.max_id = str(int(entry.id_str) - 1)

        redis.flush_buffer()

    def _entries_to_apitwitterentries(self):
        """
        Iter over all entries in the response.
        Each entry in the response is converted to a `ApiTwitterEntry` instance.
        """

        rj = self.response.json()

        def _lpop():
            """
            Pop from the head of the list.
            Convert the item to `ApiTwitterEntry`.
            """
            while True:
                try:
                    entry = rj.pop(0)
                    entry = ApiTwitterEntry(entry)
                    return entry
                except IndexError:
                    # `self.response` is empty, return None to stop the iter
                    return None

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)
