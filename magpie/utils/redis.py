from abc import ABCMeta

import redis

from magpie.settings import settings
from .exceptions import ImproperlyConfigured
from .exceptions import RedisDownloadEntryInconsistentError

pool = 0


def open_redis_connection():
    """
    Generic function to call in order to talk to Redis. It is build such as it uses a unique
    connection pool (in case of TCP socket connection, while no connection pool in required
    in case of unix socket connection).
    Use it like this:
        redis = open_redis_connection()
        print(redis.info())
    """
    global pool

    if 'TCP_SOCKET' in settings.REDIS:
        if pool == 0:
            pool = _build_connection_pool()
        # TODO change this prints to log.debug to console
        print("+++++++++++++++++++++++++++ Opening a connection to Redis")
        return redis.StrictRedis(connection_pool=pool)

    if 'UNIX_SOCKET' in settings.REDIS:
        print("+++++++++++++++++++++++++++ Opening a connection to Redis")
        return redis.Redis(unix_socket_path=settings.REDIS['UNIX_SOCKET']['PATH'])

    raise ImproperlyConfigured('You must set proper Redis connection details in the'
                               ' settings file.')


def _build_connection_pool():
    print("+++++++++++++++++++++++++++ Building a connection pool to Redis")
    if 'TCP_SOCKET' in settings.REDIS:
        return redis.ConnectionPool(
            host=settings.REDIS['TCP_SOCKET']['HOST'],
            port=settings.REDIS['TCP_SOCKET']['PORT'],
            db=settings.REDIS['TCP_SOCKET']['DB']
        )
    return None


class AbstractRedisList(metaclass=ABCMeta):
    """
    Abstract class to manage a single list (queue) in Redis.
    """
    @property
    def _pipeline(self):
        """
        Redis list pipeline getter. A pipeline is a buffer.
        """
        try:
            b = self._pipeline_cache
        except AttributeError:
            r = open_redis_connection()
            b = self._pipeline_cache = r.pipeline()
        return b

    @_pipeline.setter
    def _pipeline(self, value):
        """
        Redis list pipeline setter: it opens the pipeline only when first needed. A pipeline is a
        buffer.
        """
        self._pipeline_cache = value

    def buffer(self, entry):
        """
        Add a entry to this Redis list (through a pipeline, which is a buffer).
        `entry` must have 2 string attributes: operation_type and remote_path and it will be
        saved in Redis w/ the syntax: b"+/dir1/file2.txt".

        Parameter:
        entry -- a `DropboxResponseEntry` or `RedisEntry` instance or any other object with two
        attributes: operation_type and remote_path.
        """
        # TODO
        print("Storing {} in Redis.".format(entry))

        self._pipeline.rpush(
            self._list_name,
            '{}{}'.format(entry.operation_type, entry.remote_path)
        )

    def flush_buffer(self):
        """
        Flush the pipeline (Redis' buffer) to Redis.
        """
        if self._pipeline:
            self._pipeline.execute()

    def iterate(self):
        """
        Iterate over the Redis list.
        Return a iterator object which iterates over `RedisEntry` objects.
        """
        r = open_redis_connection()

        def _lpop():
            """
            Pop from the head of the Redis list.
            Convert the item to `RedisEntry`.
            """
            entry = r.lpop(self._list_name)
            if entry:
                entry = RedisEntry(entry)
            return entry

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)


class RedisDownloadList(AbstractRedisList):
    """
    A Redis list which maps Dropbox files.
    Entries of the list in Redis have this form: "+/dir1/file2.txt".
    The first char can be:
      '+' if it is a file to download
      '-' if it is a file to delete
    'XRESET' means that the entire Dropbox root folder must be deleted.
    """
    def __init__(self, bearertoken_id):
        self._list_name = 'token:{}:dw'.format(bearertoken_id)

    def buffer_add_reset(self):
        """
        Add a reset instruction to Redis' download list (through a pipeline which is a buffer).
        """
        self._pipeline.rpush(self._list_name, 'XRESET')


class RedisIndexList(AbstractRedisList):
    """
    A Redis list which maps files to index with Solr.
    Entries of the list in Redis have this form: "+/dir1/file2.txt".
    The first char can be:
      '+' if it is a file already downloaded locally and ready to be indexed
      '-' if it is a file to delete from the index
    'XRESET' means that the entire index must be deleted.
    """
    def __init__(self, bearertoken_id):
        self._list_name = 'token:{}:ix'.format(bearertoken_id)


class RedisEntry:
    """
    A entry of a Redis download list.

    Parameters:
    redis_bytes_string -- a original entry of a Redis download list, like: b"+/dir1/file2.txt"
    It is a bytes string in Python.
    """
    def __init__(self, redis_bytes_string):
        self.operation_type = redis_bytes_string[:1].decode(encoding='UTF-8')
        self.remote_path = redis_bytes_string[1:].decode(encoding='UTF-8')
        self._sanity_check()

    def _sanity_check(self):
        """
        `redis_dw_entry` is a `RedisEntry` instance.
        A `redis_dw_entry` is consistent if:
            - `operation` is: '+' or '-' or 'X'.
            - `remote_path` is 'RESET' if `operation` is 'X'.
        """
        if not self.operation_type in ['+', '-', 'X']:
            raise RedisDownloadEntryInconsistentError("The operation must be '+', '-' or 'X'.")

        if self.operation_type == 'X' and not self.remote_path == 'RESET':
            raise RedisDownloadEntryInconsistentError("If the operation is 'X' the remote_path"
                                                      "must be 'REST'.")

    def __str__(self):
        return '<{}(operation_type={}, remote_path={})>'.format(
            self.__class__.__name__, self.operation_type, self.remote_path
        )