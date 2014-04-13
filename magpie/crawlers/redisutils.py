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
    def __init__(self):
        self._download_buffer = None

    def add_to_download_buffer(self, entry, bearertoken_id):
        """
        Add `DropboxResponseEntry` to the download pipeline (Redis' buffer).
        Each entry in the download pipeline maps a file to be downloaded from Dropbox.
        """
        print("Storing {} in Redis with bearertoken_id={}".format(entry, bearertoken_id))

        if not self._download_buffer:
            r = open_redis_connection()
            self._download_buffer = r.pipeline()

        self._download_buffer.rpush(
            'token:{}'.format(bearertoken_id),
            '{}{}'.format(entry.operation_type, entry.path)
        )

    def flush_download_buffer(self):
        """
        Flush the download pipeline (Redis' buffer) to Redis.
        Each entry in the download pipeline maps a file to be downloaded from Dropbox.
        """
        if self._download_buffer:
            self._download_buffer.execute()

