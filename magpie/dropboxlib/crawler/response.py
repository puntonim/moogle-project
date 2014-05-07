import logging
import json

from ..redislist import RedisDropboxDownloadList
from ..entry import ApiDropboxEntry
from response import AbstractApiResponse


log = logging.getLogger('dropbox')


class ApiDropboxResponse(AbstractApiResponse):
    """
    A response got back from Dropbox after an update query.
    It is build from the parameter `response` which is a Python dictionary.

    Parameters:
    `response` -- a Python dictionary like the following example.
    The `entries` key contains a set of up to about 1k entries, where each entry is a file
    added or removed to Dropbox by its owner. Each of this entry will be mapped to a
    `ApiDropboxEntry`.
    The `has_more` key shows whether the response is not complete, by meaning that more items
    will be included in the response to the next update query.
    {
        "cursor": "AAFP6m8ToJqE...BgNY7qD3VOKgfxA",
        "has_more": false,
        "reset": true,
        "entries": [
            [
                "/temp/moogletest",
                {
                    "bytes": 0,
                    "revision": 241716,
                    "modified": "Mon, 27 Jan 2014 20:17:24 +0000",
                    "size": "0 bytes",
                    "root": "dropbox",
                    "is_dir": true,
                    "thumb_exists": false,
                    "path": "/temp/moogletest",
                    "rev": "3b0340265d3a0",
                    "icon": "folder"
                }
            ],
            ...
        ]
    }
    """
    def __init__(self, response):
        super().__init__(response)
        # `is_reset` shows that we need to delete all the entry we have stored for the
        # current user.
        self.is_reset = self.response.get('reset', False)
        self.has_more = self.response.get('has_more', False)
        # The cursor is the identifier used by Dropbox to keep track of the point in time of the
        # last synchronization. Say we synchronized last time yesterday at 6pm and got a cursor.
        # If we synchronize again today using the same cursor, we will get only the updates
        # happened after yesterday 6pm.
        self.updates_cursor = self.response.get('cursor', '')

        log.debug('Response got: \n{}'.format(json.dumps(response, indent=4)))

    def _init_redis_list(self, *args, **kwargs):
        return RedisDropboxDownloadList(*args, **kwargs)

    def _hook_parse_entire_response(self, redis):
        if self.is_reset:
            redis.buffer_add_reset()

    def _extract_entries_list(self):
        return self.response.get('entries', list())

    def _init_api_provider_entry(self, *args, **kwargs):
        return ApiDropboxEntry(*args, **kwargs)

    def _sanity_check(self):
        """
        Override default `_sanity_check` from `AbstractApiResponse`. We don't need a sanity check
        because we are using the specific `dropbox` library here and not the generic
        `request_oauthlib`. This library raise an exception in case of error, so we don't need
        to perform a sanity check ourself.
        """
        pass

    def _build_pagination_cursor(self):
        pass

    def _build_updates_cursor(self):
        pass
