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
            }
        )


    def iterate(self):
        pass