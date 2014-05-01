from abc import ABCMeta

from utils.redis import AbstractRedisList, open_redis_connection


class RedisTwitterList(AbstractRedisList, metaclass=ABCMeta):
    """
    List (queue) of Twitter tweets in Redis.
    """

    def __init__(self, bearertoken_id):
        self._list_name = 'twitter:token:{}'.format(bearertoken_id)

    def buffer(self, entry):
        """

        Parameters:
        entry -- A `TwitterResponseEntry` instance.
        """
        # TODO
        print("Storing {} in Redis.".format(entry))

        self._pipeline.rpush(
            self._list_name,
            '{}'.format(entry.id_str)
        )

        self._pipeline.hmset(
            '{}:{}'.format(self._list_name, entry.id_str),
            {
                'text': entry.text,
                'lang': entry.lang,
                'created_at': entry.created_at,
                'text_clean': entry.text_clean,
            }
        )

    def iterate(self):
        """
        Iterate over the Redis list.
        Return an iterator object which iterates over `RedisTwitterEntry` objects.
        """
        r = open_redis_connection()
        pipeline = r.pipeline()

        def _lpop():
            """
            Pop from the head of the Redis list..............
            Convert the item to `RedisDropboxEntry`.
            """
            tweet_id = r.lpop(self._list_name)
            if not tweet_id:
                return None

            hash_name = '{}:{}'.format(self._list_name, tweet_id.decode(encoding='UTF-8'))
            tweet_dict = r.hgetall(hash_name)
            # Delete the hash through a pipeline. The use of a pipeline is to avoid a sort
            # of bug. The bug was the following:
            # entry = r.hgetall(hash_name)  -- READ
            # r.delete(hash_name)           -- DELETE
            # Sometimes the DELETE happens before the READ causing the read value to be None: this
            # is very very weird, but it happened sometimes. Using a pipeline solve this.
            pipeline.delete(hash_name)

            return RedisTwitterEntry(tweet_id, tweet_dict)

        def _lpop_mgr():
            """
            Wrap _lpop in a try-except block to make sure the pipeline is executed even in case
            of exception.
            """
            try:
                item = _lpop()
                if not item:
                    pipeline.execute()
                return item
            except:
                pipeline.execute()
                raise

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop_mgr, None)


class RedisTwitterEntry:
    """
    A Twitter entry (tweet) of a Redis list.
    """

    def __init__(self, tweet_id, tweet_dict):
        self.id = tweet_id.decode(encoding='UTF-8')
        self.lang = tweet_dict[b'lang'].decode(encoding='UTF-8')
        self.created_at = tweet_dict[b'created_at'].decode(encoding='UTF-8')
        self.text = tweet_dict[b'text'].decode(encoding='UTF-8')
        self.text_clean = tweet_dict[b'text_clean'].decode(encoding='UTF-8')
