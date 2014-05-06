from .entry import RedisTwitterEntry
from redislist import AbstractRedisList, open_redis_connection


class RedisTwitterList(AbstractRedisList):
    """
    List (queue) of Twitter tweets in Redis.
    """
    @staticmethod
    def _build_list_name(bearertoken_id):
        return 'twitter:token:{}'.format(bearertoken_id)

    def buffer(self, entry):
        """

        Parameters:
        entry -- A `ApiTwitterEntry` instance.
        """
        # TODO
        print("Storing {} in Redis.".format(entry))

        self._pipeline.rpush(
            self._list_name,
            '{}'.format(entry.id)
        )

        self._pipeline.hmset(
            '{}:{}'.format(self._list_name, entry.id),
            {
                'text': entry.text,
                'lang': entry.lang,
                'created_at': entry.created_at,
                'retweeted': entry.retweeted,
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
            Pop from the head of the Twitter Redis list and get the hash entry.
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
