from os.path import splitext, basename
from abc import ABCMeta
import hashlib

from utils.exceptions import InconsistentItemError, EntryNotToBeIndexed
from magpie.settings import settings
from redislist import AbstractRedisEntry


class BaseDropboxEntry(metaclass=ABCMeta):
    __all__ = ['id', 'path', 'operation']


class ApiDropboxEntry(BaseDropboxEntry):
    """
    A response got back from Dropbox is a Python dictionary (which is mapped to a
    `DropboxResponse`). This dictionary contains a `entries` key, which is a Python list of up to
    about 1k entries where each entry is a file added or removed to Dropbox by its owner.
    Each of this entry is mapped to a `ApiDropboxEntry`.

    Parameters:
    entry_list -- a file added or removed to Dropbox by its owner. It is a Python list made of 2
    elements:
     - remote_path: a Python string which maps the remote path of the file.
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
        self._filter()
        self.id = self._build_id(self.path)
        self.operation = self._find_operation()


    @staticmethod
    def _sanity_check(entry_list):
        """
        Sanity check to make sure this `entry_list` is a valid entry.
        """
        if not len(entry_list) == 2:
            raise InconsistentItemError("This entry is not a list with 2 elements.")

        remote_path = entry_list[0]
        metadata = entry_list[1]  # None if the operation is delete.

        if not remote_path:
            raise InconsistentItemError("This entry has no remote path.")

        if not isinstance(remote_path, str):
            raise InconsistentItemError("The remote path of this entry is not a string.")

        return remote_path, metadata

    def _filter(self):
        """
        Filter based on rules as follows:
        a. If it is a deletion, then there is no metadata, so we don't know if the file is a file
           or a dir (a dir can be named 'mydir.txt' and a file can be named 'myfile' so we cannot
           guess it simply from the name) -> It is a valid entry (in Solr we will then delete
           file_name and file_name/*).
        b. If it is a dir (and it can only be an addition, since we know that it is a dir from the
           metadata and the presence of the metadata means it is an addition) -> It is NOT a valid
           entry, raise an exception.
        c. If its size is > settings.DROPBOX_MAX_FILE_SIZE -> It is NOT a valid entry, raise an
           exception.
        d. If it has inconsistent metadata -> It is a NOT valid entry, raise an exception.
        e. If the file extension is not in settings.DROPBOX_FILE_EXT_FILTER -> It is NOT a valid
           entry, raise an exception.
        f. In all the other cases -> It is a valid entry.
        """
        # If there is a metadata,
        #   and it is not a dir (so it's a file),
        #   and its size is allowed,
        # then it is a file to add.
        if self.metadata:
            try:
                is_dir = self.metadata['is_dir']
                size = self.metadata['bytes']
                path = self.metadata['path']
            except KeyError as e:  # Case d.
                raise InconsistentItemError('Some metadata are missing.') from e

            try:
                ext = splitext(basename(path))[1][1:].lower()
            except Exception as e:  # Case d.
                raise InconsistentItemError('The file extension is not consistent.') from e

            # Cases b., c., e.
            if is_dir or \
               size > settings.DROPBOX_MAX_FILE_SIZE or \
               ext not in settings.DROPBOX_FILE_EXT_FILTER:
                raise EntryNotToBeIndexed

            # Case a., f.: nothing to do

    @staticmethod
    def _build_id(text):
        return hashlib.md5(text.encode()).hexdigest()

    def _find_operation(self):
        """
        Find out if this `entry_list` is a file added ('+') or deleted ('-').
        """
        # If there is no metadata it is a file to delete, otherwise it is a file to add
        if not self.metadata:
            return '-'
        return '+'

    def __str__(self):
        return '<{}(remote_path={}, operation={})>'.format(
            self.__class__.__name__, self.path, self.operation
        )


class RedisDropboxEntry(BaseDropboxEntry, AbstractRedisEntry):
    """
    A Dropbox entry of a Redis list.

    Parameters:
    entry -- a original entry of a Redis list, like: b"+/dir1/file2.txt". It is a bytes string
    in Python.
    """
    def _sanity_check(self):
        """
        A `RedisDropboxEntry` instance is consistent if:
            - `operation` is: '+' or '-' or 'X'.
            - `remote_path` is 'RESET' if `operation` is 'X'.
        """
        if not self.operation in ['+', '-', 'X']:
            raise InconsistentItemError("The operation must be '+', '-' or 'X'.")

        if self.operation == 'X' and not self.path == 'RESET':
            raise InconsistentItemError("If the operation is 'X' the remote_path"
                                        "must be 'REST'.")

    def is_add(self):
        """True if the `operation` is '+'."""
        return self.operation == '+'

    def is_del(self):
        """True if the `operation` is '-'."""
        return self.operation == '-'

    def is_reset(self):
        """True if the `operation` is 'X' and remote_path is 'RESET'."""
        return self.path == 'RESET'

    def __str__(self):
        return '<{}(operation={}, remote_path={})>'.format(
            self.__class__.__name__, self.operation, self.path
        )