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
        print("+++++++++++++++++++++++++++ Opening a TCP connection to Redis")
        return redis.StrictRedis(connection_pool=pool)

    if 'UNIX_SOCKET' in settings.REDIS:
        print("+++++++++++++++++++++++++++ Opening a SOCKET connection to Redis")
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