from abc import ABCMeta, abstractmethod

from utils.redis import open_redis_connection


class AbstractRedisList(metaclass=ABCMeta):
    """
    Abstract class to manage a single list (queue) in Redis.
    """
    def __init__(self, bearertoken_id):
        self._list_name = self._build_list_name(bearertoken_id)

    @staticmethod
    @abstractmethod
    def _build_list_name(bearertoken_id):
        pass

    @property
    def _pipeline(self):
        """
        Redis list pipeline getter. A pipeline is a buffer.
        """
        try:
            b = self._pipeline_cache
        except AttributeError:
            r = open_redis_connection()
            b = self._pipeline_cache = r.pipeline()
        return b

    @_pipeline.setter
    def _pipeline(self, value):
        """
        Redis list pipeline setter: it opens the pipeline only when first needed. A pipeline is a
        buffer.
        """
        self._pipeline_cache = value

    @abstractmethod
    def buffer(self, entry):
        """
        Add a entry to this Redis list (through a pipeline, which is a buffer).

        Parameter:
        entry -- the entry to be added.
        """
        pass

    @staticmethod
    def _is_indexable(entry):
        """
        Decide whether an entry has to be indexed or not.
        """
        return True

    def flush_buffer(self):
        """
        Flush the pipeline (Redis' buffer) to Redis.
        """
        if self._pipeline:
            self._pipeline.execute()

    @abstractmethod
    def iterate(self):
        """
        Iterate over the Redis list.
        """
        pass


class AbstractRedisEntry(metaclass=ABCMeta):
    """
    A entry (Facebook post, Twitter tweet, Dropbox file, ...) stored in Redis.

    Parameters:
    entry_id -- a string, the id of the entry.
    entry_dict -- a Python dictionary, f.i. a Facebook post like:
        {
            b'from_name': 'Paulo Van Der Kofje',
            b'from_id': '1522956429',
            b'type': 'status',
            b'created_time': '2014-05-01T16:59:41+0000',
            b'updated_time': '2014-05-01T16:59:41+0000',
            b'message': 'test message'
        }
    """
    __all__ = ['id',]

    def __init__(self, entry_id, entry_dict):
        self.id = entry_id.decode(encoding='UTF-8')

        field_names = list(self.__all__)
        field_names.remove('id')
        for field_name in field_names:
            try:
                self.__setattr__(field_name, entry_dict[field_name.encode()].decode('UTF-8'))
            except Exception as e:
                import bpdb; bpdb.set_trace()