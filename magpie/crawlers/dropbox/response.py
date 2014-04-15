from ..redisutils import RedisStore


class DropboxResponse:
    """
    A response got back from Dropbox after an update query.
    It is build out of a the parameter `response_dict` which is a Python dictionary.

    Parameters:
    `response_dict` -- a Python dictionary like the following example.
    The `entries` key contains a set of up to about 1k entries, where each entry is a file
    added or removed to Dropbox by its owner. Each of this entry will be mapped to a
    `DropboxResponseEntry`.
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

    def __init__(self, response_dict):
        self.response_dict = response_dict

    @property
    def updates_cursor(self):
        """
        The cursor is the identifier used by Dropbox to keep track of the point in time of the
        last synchronization. Say we synchronized last time yesterday at 6pm and got a cursor.
        If we synchronize again today using the same cursor, we will get only the updates happened
        after yesterday 6pm.
        """
        return self.response_dict.get('cursor', '')

    @property
    def is_reset(self):
        """
        Show that we need to delete all the entry we have stored for the current user.
        """
        return self.response_dict.get('reset', False)

    @property
    def has_more(self):
        """
        Show that there are more entries to be retrieved with a new update query.
        """
        return self.response_dict.get('has_more', False)

    def parse(self, bearertoken_id):
        """
        Parse a response got back from Dropbox after an update query.
        Create a `RedisStore` for the current `bearertoken_id` and add each entry of the
        `response_dict['entries']` list to the download list of the `RedisStore`.

        Parameters:
        bearertoken_id -- the identifier to bind this response to a Dropbox user (using his
        `BearerToken`.
        """

        redis_store = RedisStore(bearertoken_id)

        if self.is_reset:
            redis_store.add_reset()

        for entry_list in self.response_dict.get('entries', list()):
            redis_store.add_to_download_list_buffer(entry_list)
        redis_store.flush_download_list_buffer()

