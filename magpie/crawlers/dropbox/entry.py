from ..exceptions import InconsistentItemError, EntryNotToBeIndexed
from magpie.settings import settings


class DropboxResponseEntry:
    """
    A response got back from Dropbox is a Python dictionary (which is mapped to a
    `DropboxResponse`). This dictionary contains a `entries` key, which is a Python list of up to
    about 1k entries where each entry is a file added or removed to Dropbox by its owner.
    Each of this entry is mapped to a `DropboxResponseEntry`.

    Parameters:
    entry_list -- a file added or removed to Dropbox by its owner. It is a Python list made of 2
    elements:
     - path: a Python string which maps the path of the file.
     - metadata: a Python dictionary with metadata about the file.
    There can be 3 different cases:
        1) A directory to add:
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
        ]
        2) A file to add:
        [
            "/temp/moogletest/uno.txt",
            {
                "mime_type": "text/plain",
                "bytes": 205,
                "thumb_exists": false,
                "modified": "Mon, 27 Jan 2014 21:09:36 +0000",
                "size": "205 bytes",
                "path": "/temp/moogletest/uno.txt",
                "icon": "page_white_text",
                "client_mtime": "Wed, 14 Mar 2012 00:02:51 +0000",
                "root": "dropbox",
                "is_dir": false,
                "revision": 241780,
                "rev": "3b0740265d3a0"
            }
        ]
        3) A file or directory to delete:
        [
            "/temp/moogletest/tre/myfile.txt",
            null
        ]
    """

    def __init__(self, entry_list):
        self.path, self.metadata = self._sanity_check(entry_list)
        self.operation_type = self._find_operation_type()

    def _sanity_check(self, entry_list):
        """
        Sanity check to make sure this `entry_list` is a valid entry.
        """
        if not len(entry_list) == 2:
            raise InconsistentItemError("This entry is not a tuple with 2 elements.")

        path = entry_list[0]
        metadata = entry_list[1]

        if not path:
            raise InconsistentItemError("This entry has no path.")

        if not isinstance(path, str):
            raise InconsistentItemError("The path of this entry is not a string.")

        return path, metadata

    def _find_operation_type(self):
        """
        Find out if this `entry_list` is a file/dir added ('+') or deleted ('-').
        """
        # If there is no metadata it is a file to delete
        if not self.metadata:
            return '-'

        # If there is a metadata,
        #   and it is not a dir (so it's a file),
        #   and its size is allowed,
        # then it is a file to add.
        try:
            is_dir = self.metadata['is_dir']
            size = self.metadata['bytes']
        except KeyError as e:
            raise InconsistentItemError('Some metadata are missing.') from e
        if is_dir or size > settings.DROPBOX_MAX_FILE_SIZE:
            raise EntryNotToBeIndexed
        return '+'

    def __str__(self):
        return '<{}(path={}, operation={})>'.format(
            self.__class__.__name__, self.path, self.operation_type
        )
