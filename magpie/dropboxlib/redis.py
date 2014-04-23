from abc import ABCMeta

from utils.redis import AbstractRedisList, open_redis_connection
from utils.exceptions import RedisDropboxEntryInconsistentError


class AbstractRedisDropboxList(AbstractRedisList, metaclass=ABCMeta):
    """
    Abstract class to manage a single Dropbox list (queue) in Redis.
    """
    def buffer(self, entry):
        """
        Add a entry to this Redis list (through a pipeline, which is a buffer).
        `entry` must have 2 string attributes: operation_type and remote_path and it will be
        saved in Redis w/ the syntax: b"+/dir1/file2.txt".

        Parameter:
        entry -- a `DropboxResponseEntry` or `RedisDropboxEntry` instance or any other object
        with two attributes: operation_type and remote_path.
        """
        # TODO
        print("Storing {} in Redis.".format(entry))

        self._pipeline.rpush(
            self._list_name,
            '{}{}'.format(entry.operation_type, entry.remote_path)
        )

    def iterate(self):
        """
        Iterate over the Redis list.
        Return an iterator object which iterates over `RedisDropboxEntry` objects.
        """
        r = open_redis_connection()

        def _lpop():
            """
            Pop from the head of the Redis list.
            Convert the item to `RedisDropboxEntry`.
            """
            entry = r.lpop(self._list_name)
            if entry:
                entry = RedisDropboxEntry(entry)
            return entry

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)


class RedisDropboxDownloadList(AbstractRedisDropboxList):
    """
    A Redis list which maps Dropbox files.
    Entries of the list in Redis have this form: "+/dir1/file2.txt".
    The first char can be:
      '+' if it is a file to download
      '-' if it is a file to delete
    'XRESET' means that the entire Dropbox root folder must be deleted.
    """
    def __init__(self, bearertoken_id):
        self._list_name = 'dropbox:token:{}:dw'.format(bearertoken_id)

    def buffer_add_reset(self):
        """
        Add a reset instruction to Redis' download list (through a pipeline which is a buffer).
        """
        self._pipeline.rpush(self._list_name, 'XRESET')


class RedisDropboxIndexList(AbstractRedisDropboxList):
    """
    A Redis list which maps files to index with Solr.
    Entries of the list in Redis have this form: "+/dir1/file2.txt".
    The first char can be:
      '+' if it is a file already downloaded locally and ready to be indexed
      '-' if it is a file to delete from the index
    'XRESET' means that the entire index must be deleted.
    """
    def __init__(self, bearertoken_id):
        self._list_name = 'dropbox:token:{}:ix'.format(bearertoken_id)


class RedisDropboxEntry:
    """
    A Dropbox entry of a Redis list.

    Parameters:
    entry -- a original entry of a Redis list, like: b"+/dir1/file2.txt". It is a bytes string
    in Python.
    """
    def __init__(self, entry):
        self.operation_type = entry[:1].decode(encoding='UTF-8')
        self.remote_path = entry[1:].decode(encoding='UTF-8')
        self._sanity_check()

    def _sanity_check(self):
        """
        A `RedisDropboxEntry` instance is consistent if:
            - `operation` is: '+' or '-' or 'X'.
            - `remote_path` is 'RESET' if `operation` is 'X'.
        """
        if not self.operation_type in ['+', '-', 'X']:
            raise RedisDropboxEntryInconsistentError("The operation must be '+', '-' or 'X'.")

        if self.operation_type == 'X' and not self.remote_path == 'RESET':
            raise RedisDropboxEntryInconsistentError("If the operation is 'X' the remote_path"
                                                      "must be 'REST'.")

    def is_add(self):
        """True if the `operation_type` is '+'."""
        return self.operation_type == '+'

    def is_del(self):
        """True if the `operation_type` is '-'."""
        return self.operation_type == '-'

    def is_reset(self):
        """True if the `operation_type` is 'X' and remote_path is 'RESET'."""
        return self.remote_path == 'RESET'

    def __str__(self):
        return '<{}(operation_type={}, remote_path={})>'.format(
            self.__class__.__name__, self.operation_type, self.remote_path
        )