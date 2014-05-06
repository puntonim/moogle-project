from .entry import RedisFacebookEntry
from redislist import AbstractRedisList


class RedisFacebookList(AbstractRedisList):
    """
    List (queue) of Facebook posts in Redis.
    """
    @staticmethod
    def _build_list_name(bearertoken_id):
        return 'facebook:token:{}'.format(bearertoken_id)

    @staticmethod
    def _init_redis_provider_entry(*args, **kwargs):
        return RedisFacebookEntry(*args, **kwargs)