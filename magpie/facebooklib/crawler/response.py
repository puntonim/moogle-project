from datetime import datetime
from calendar import timegm
import logging
import json

from utils.exceptions import FacebookResponseError
from ..entry import ApiFacebookEntry
from ..redis import RedisFacebookList


log = logging.getLogger('facebook')


class ApiFacebookResponse:
    """

    Parameters:
    response -- a `requests.models.Response` instance.
    """

    def __init__(self, response):
        self.response = response
        self.updates_cursor = ''
        self.has_more = False
        self.next = ''

        log.debug('Response got: {}\n{}'.format(self.response.status_code,
                                                json.dumps(self.response.json(), indent=4)))
        self._sanity_check()

    def _sanity_check(self):
        """
        Check whether the current response got from Facebook is an error response.
        """
        # If the HTTP status code is not 200, then it is an error.
        # https://developers.facebook.com/docs/graph-api/using-graph-api/#errors
        if self.response.status_code != 200:
            msg = 'HTTP Status: {}\n{}'.format(self.response.status_code, self.response.json())
            raise FacebookResponseError(msg)
        # TODO implement a check on rate limit error

    def parse(self, bearertoken_id):
        redis = RedisFacebookList(bearertoken_id)

        # Pagination: next parameter.
        self._build_next_parameter()

        is_first_entry = True  # for updates cursor
        for entry in self._entries_to_apifacebookentries():
            # `entry` is a `ApiFacebookEntry` instance.

            #print(entry.id, entry.message)
            redis.buffer(entry)

            # Pagination: cursor (the `updated_time` of the most recent post).
            if is_first_entry:
                self._build_updates_cursor(entry)
                is_first_entry = False

        redis.flush_buffer()

    def _build_next_parameter(self):
        rj = self.response.json()
        data = rj.get('paging', {})
        self.next = data.get('next', '')
        if self.next:
            self.has_more = True

    def _build_updates_cursor(self, entry):
        # The `updated_time` of the most recent post is what we must use as cursor.
        # We need to convert it to unix time tho.
        datestamp = datetime.strptime(entry.updated_time, '%Y-%m-%dT%H:%M:%S+0000')
        self.updates_cursor = timegm(datestamp.utctimetuple())  # Conversion to unix time.

    def _entries_to_apifacebookentries(self):
        """
        Iter over all entries in the response.
        Each entry in the response is converted to a `ApiFacebookEntry` instance.
        """

        rj = self.response.json()
        data = rj.get('data', list())

        def _lpop():
            """
            Pop from the head of the list.
            Convert the item to `ApiFacebookEntry`.
            """
            while True:
                try:
                    entry = data.pop(0)  # Raise IndexError when completely consumed.
                    entry = ApiFacebookEntry(entry)
                    return entry
                except IndexError:
                    # `self.response` is empty, return None to stop the iter.
                    return None

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)