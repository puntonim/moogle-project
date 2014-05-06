from datetime import datetime
from calendar import timegm
import logging
import json

from utils.exceptions import FacebookResponseError
from ..entry import ApiFacebookEntry
from ..redis import RedisFacebookList
from response import AbstractApiResponse


log = logging.getLogger('facebook')


class ApiFacebookResponse(AbstractApiResponse):
    """
    Response got after a query to Facebook.

    Parameters:
    response -- a `requests.models.Response` instance.
    """
    def _sanity_check(self):
        """
        Check whether the current response got from Facebook is an error response.
        """
        log.debug('Response got: {}\n{}'.format(self.response.status_code,
                                                json.dumps(self.response.json(), indent=4)))

        # If the HTTP status code is not 200, then it is an error.
        # https://developers.facebook.com/docs/graph-api/using-graph-api/#errors
        if self.response.status_code != 200:
            msg = 'HTTP Status: {}\n{}'.format(self.response.status_code, self.response.json())
            raise FacebookResponseError(msg)
        # TODO implement a check on rate limit error

    def _init_redis_list(self, bearertoken_id):
        return RedisFacebookList(bearertoken_id)

    def _hook_parse_entire_response(self):
        # Pagination cursor: the `next` key of this page.
        self._build_pagination_cursor()

    def _build_pagination_cursor(self):
        """The pagination cursor for Facebook is the `next` parameter."""
        rj = self.response.json()
        data = rj.get('paging', {})
        self.pagination_cursor = data.get('next', '')
        if self.pagination_cursor:
            self.has_more = True

    def _hook_parse_first_entry(self, entry):
        self._build_updates_cursor(entry)

    def _build_updates_cursor(self, entry):
        # The `updated_time` of the most recent post is what we must use as cursor.
        # We need to convert it to unix time tho.
        datestamp = datetime.strptime(entry.updated_time, '%Y-%m-%dT%H:%M:%S+0000')
        self.updates_cursor = timegm(datestamp.utctimetuple())  # Conversion to unix time.

    def _hook_parse_last_entry(self):
        pass

    def _init_api_provider_entry(self, entry):
        return ApiFacebookEntry(entry)

    @staticmethod
    def _extract_entries_list(data_dict):
        return data_dict.get('data', list())