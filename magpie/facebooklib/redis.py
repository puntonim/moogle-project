from abc import ABCMeta

from utils.redis import AbstractRedisList, open_redis_connection


class RedisFacebookList(AbstractRedisList, metaclass=ABCMeta):
    """
    List (queue) of Facebook statuses in Redis.
    """

    def __init__(self, bearertoken_id):
        self._list_name = 'facebook:token:{}'.format(bearertoken_id)

    def buffer(self, entry):
        """

        Parameters:
        entry -- A `FacebookResponseEntry` instance.
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
                'updated_time': entry.updated_time,
                'message': entry.message,
            }
        )

    def iterate(self):
        """
        Iterate over the Redis list.
        Return an iterator object which iterates over `RedisFacebookEntry` objects.
        """
        r = open_redis_connection()
        pipeline = r.pipeline()

        def _lpop():
            """
            Pop from the head of the Facebook Redis list and get the hash entry.
            Convert the pop and hash items to a `RedisFacebookEntry` instance.
            """
            post_id = r.lpop(self._list_name)
            if not post_id:  # The list has been completely consumed.
                return None

            hash_name = '{}:{}'.format(self._list_name, post_id.decode(encoding='UTF-8'))
            post_dict = r.hgetall(hash_name)
            # Delete the hash through a pipeline. The use of a pipeline is to avoid a sort
            # of bug. The bug was the following:
            # entry = r.hgetall(hash_name)  -- READ
            # r.delete(hash_name)           -- DELETE
            # Sometimes the DELETE happens before the READ causing the read value to be None: this
            # is very very weird, but it happened sometimes. Using a pipeline solve this.
            pipeline.delete(hash_name)
            return RedisFacebookEntry(post_id, post_dict)

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


class RedisFacebookEntry:
    """
    A Facebook entry (post) of a Redis list.
    """
    def __init__(self, post_id, post_dict):
        self.id = post_id.decode(encoding='UTF-8')
        self.message = post_dict[b'message'].decode(encoding='UTF-8')
        self.updated_time = post_dict[b'updated_time'].decode(encoding='UTF-8')