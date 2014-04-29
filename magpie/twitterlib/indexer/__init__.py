from ..redis import RedisTwitterList


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

            print(redis_entry.id, redis_entry.text_clean)
