from abc import ABCMeta

from utils.redis import AbstractRedisList, open_redis_connection


class RedisTwitterList(AbstractRedisList, metaclass=ABCMeta):
    """
    Abstract class to manage a single list (queue) in Redis.
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
            r.delete(hash_name)

            return RedisTwitterEntry(tweet_id, tweet_dict)

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)


class RedisTwitterEntry:
    """
    A Twitter entry of a Redis list.

    Parameters:
    redis_bytes_string -- a original entry of a Redis list, like: b"+/dir1/file2.txt"
    It is a bytes string in Python.
    """

    def __init__(self, tweet_id, tweet_dict):
        self.id = tweet_id.decode(encoding='UTF-8')
        self.lang = tweet_dict[b'lang'].decode(encoding='UTF-8')
        self.created_at = tweet_dict[b'created_at'].decode(encoding='UTF-8')
        self.text = tweet_dict[b'text'].decode(encoding='UTF-8')
        self.text_clean = tweet_dict[b'text_clean'].decode(encoding='UTF-8')
