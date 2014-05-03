import logging

from ..redis import RedisTwitterList


log = logging.getLogger('twitter')


class TwitterIndexer:
    """
    ...
    """

    def __init__(self, bearertoken_id, access_token):
        self.bearertoken_id = bearertoken_id
        self.access_token = access_token

    def run(self):
        """
        ....
        """
        redis = RedisTwitterList(self.bearertoken_id)
        for redis_entry in redis.iterate():
            # `redis_entry` is a `RedisTwitterEntry` instance.

            log.debug('id={}\n'.format(redis_entry.id) +
                      'lang={}\n'.format(redis_entry.lang) +
                      'created_at={}\n'.format(redis_entry.created_at) +
                      'text={}\n'.format(redis_entry.text) +
                      'text_clean={}\n'.format(redis_entry.text_clean)
            )