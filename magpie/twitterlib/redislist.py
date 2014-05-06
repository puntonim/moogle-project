from .entry import RedisTwitterEntry
from redislist import AbstractRedisList


class RedisTwitterList(AbstractRedisList):
    """
    List (queue) of Twitter tweets in Redis.
    """
    @staticmethod
    def _build_list_name(bearertoken_id):
        return 'twitter:token:{}'.format(bearertoken_id)

    @staticmethod
    def _init_redis_provider_entry(*args, **kwargs):
        return RedisTwitterEntry(*args, **kwargs)