from ..exceptions import InconsistentItemError, EntryNotToBeIndexed
from ..redisutils import RedisStore
from .entry import DropboxResponseEntry


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
    def reset(self):
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
        Create a `DropboxResponseEntry` for each entry in `response_dict` and store them to Redis
        using `bearertoken_id` to bind each entry to its `BearerToken`.

        Every `DropboxResponseEntry` is a file which has been added or removed in Dropbox.
        In Redis the structure of a `DropboxResponseEntry` is:
            id = file path (lower case, but dropbox is case insensitive)
            operation = '+' for adding (there is no editing in Dropbox), '-' for deleting
            bearertoken_id = number to bind this entry ...

        There can be multiple operations on the same file. For instance a file might have been
        added first and then deleted, in such case Dropbox will send us 2 operations on the same
        file (in the right chronological order). The net effect is given only by the last
        operation, so this is the only operation we need to keep track.
        We can easily get this: for each item, we search in Redis if there is already an item w/
        the same id, if so we update it.

        Parameters:
        bearertoken_id -- the identifier to bind this response to a Dropbox user (using his
        `BearerToken`.
        """

        redis = RedisStore()
        for entry_list in self.response_dict.get('entries', list()):
            try:
                entry = DropboxResponseEntry(entry_list)
                redis.add_to_download_buffer(entry, bearertoken_id)
            except EntryNotToBeIndexed:
                # This is probably a dir and we don't need to index it
                continue
            except InconsistentItemError as e:
                # The current item is not consistent, like some important metadata are missing,
                # we just skip it
                # TODO log it anyway
                continue
        redis.flush_download_buffer()

