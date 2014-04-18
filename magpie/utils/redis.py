"""
This module contains 2 things:
1) The open_redis_connection() to be called anywhere in the code when we need to talk to Redis.
It is build such as it uses a unique connection pool (in case of TCP socket connection, while
no connection pool in required in case of unix socket connection). It returns a `redis.StrictRedis`
object, see: http://redis-py.readthedocs.org/en/latest/index.html#redis.StrictRedis
Use it like this:
    redis = open_redis_connection()
    print(redis.info())

2) RedisStore class with some helper methods to do some operations required by this codebase.
Use it like this:
    redis_store = RedisStore()
    redis_store.store_entry_to_be_downloaded(...)
"""

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


class RedisStore:
    """
    Class with some helper methods to do some operations required by this codebase.
    Use it like this:
        redis_store = RedisStore()
        redis_store.store_entry_to_be_downloaded(...)
    """
    def __init__(self, bearertoken_id):
        #self.bearertoken_id = bearertoken_id
        self._download_list_name = 'token:{}:dw'.format(bearertoken_id)
        self._index_list_name = 'token:{}:ix'.format(bearertoken_id)

    @property
    def _download_buffer(self):
        """
        Redis' download list pipeline getter.
        """
        try:
            dw = self._download_buffer_cache
        except AttributeError:
            r = open_redis_connection()
            dw = self._download_buffer_cache = r.pipeline()
        return dw

    @_download_buffer.setter
    def _download_buffer(self, value):
        """
        Redis' download list pipeline setter: open the pipeline only when first needed.
        """
        self._download_buffer_cache = value

    @property
    def _index_buffer(self):
        """
        Redis' index list pipeline getter.
        """
        try:
            ix = self._index_buffer_cache
        except AttributeError:
            r = open_redis_connection()
            ix = self._index_buffer_cache = r.pipeline()
        return ix

    @_index_buffer.setter
    def _index_buffer(self, value):
        """
        Redis' index list pipeline setter: open the pipeline only when first needed.
        """
        self._index_buffer_cache = value

    def add_reset(self):
        """
        Add a reset instruction to Redis' download list (through a pipeline which is a buffer).
        """
        self._download_buffer.rpush(self._download_list_name, 'XRESET')

    def _add_to_list_buffer(self, buffer, list_name, entry):
        """
        Add a `DropboxResponseEntry` or `RedisEntry` to Redis' download or index list (through
        a pipeline, which is a buffer).
        The download list and the index list are ordered lists (queue) where each entry maps a
        file to be downloaded from Dropbox or indexed by Solr.
        The syntax of each entry of a Redis' list is like: b"+/dir1/file2.txt".

        Parameter:
        buffer -- a Redis' pipeline.
        list_name -- name of the Redis' list.
        entry -- a `DropboxResponseEntry` or `RedisEntry` instance.
        """
        # TODO
        print("Storing {} in Redis.".format(entry))

        buffer.rpush(
            list_name,
            '{}{}'.format(entry.operation_type, entry.remote_path)
        )

    def add_to_download_list_buffer(self, entry):
        """
        Add a `DropboxResponseEntry` to Redis' download list (through a pipeline, which is a
        buffer).
        The download list is an ordered list (queue) where each entry maps a file to be
        downloaded from Dropbox.
        The syntax of each entry of Redis' download list is like: b"+/dir1/file2.txt".

        Parameter:
        entry -- a `DropboxResponseEntry` instance.
        """
        self._add_to_list_buffer(self._download_buffer, self._download_list_name, entry)

    def add_to_index_list_buffer(self, entry):
        """
        Add a `RedisEntry` to Redis' index list (through a pipeline, which is a
        buffer).
        The index list is an ordered list (queue) where each entry maps a file to be
        indexed by Solr.
        The syntax of each entry of Redis' index list is like: b"+/dir1/file2.txt".

        Parameters:
        entry -- a `RedisEntry` instance.
        """
        self._add_to_list_buffer(self._index_buffer, self._index_list_name, entry)

    def flush_download_list_buffer(self):
        """
        Flush the pipeline (Redis' buffer) which buffers the download list to Redis.
        Each entry in the download list maps a file to be downloaded from Dropbox.
        """
        if self._download_buffer:
            self._download_buffer.execute()

    def flush_index_list_buffer(self):
        """
        Flush the pipeline (Redis' buffer) which buffers the index list to Redis.
        Each entry in the index list maps a file to be indexed by Solr.
        """
        if self._index_buffer:
            self._index_buffer.execute()

    def _iter_over_list(self, list_name):
        """
        Iterate over the Redis download or index list for the current `bearertoken_id`.
        Return a iterator object which iterates over `RedisEntry` objects.
        It's an internal method used by `iter_over_download_list()` and
        `iter_over_index_list()`.

        Parameter:
        list_name -- name of the Redis' list.
        """
        r = open_redis_connection()

        def _lpop():
            """
            Pop from the head of the Redis list for the current `bearertoken_id`.
            Convert the item to `RedisEntry`.
            """
            entry = r.lpop(list_name)
            if entry:
                entry = RedisEntry(entry)
            return entry

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)

    def iter_over_download_list(self):
        """
        Iterate over the Redis download list for the current `bearertoken_id`.
        Usage:
            redis_store = RedisStore(self.bearertoken_id)
            for redis_dw_entry in redis_store.iter_over_download_list():
                print(redis_dw_entry.operation_type, redis_dw_entry.remote_path)
        """
        return self._iter_over_list(self._download_list_name)

    def iter_over_index_list(self):
        """
        Iterate over the Redis index list for the current `bearertoken_id`.
        Usage:
            redis_store = RedisStore(self.bearertoken_id)
            for redis_dw_entry in redis_store.iter_over_download_list():
                print(redis_dw_entry.operation_type, redis_dw_entry.remote_path)
        """
        return self._iter_over_list(self._index_list_name)


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