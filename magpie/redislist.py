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

    def buffer(self, entry):
        """
        Add a entry to this Redis list (through a pipeline, which is a buffer).

        Parameters:
        entry -- A `Api<Provider>Entry` instance to be added.
        """
        # TODO
        print("Storing {} in Redis.".format(entry))

        # Redis list to store all ids of entities
        self._pipeline.rpush(
            self._list_name,
            '{}'.format(entry.id)
        )

        # Redis hash to store all attributes of entities
        hash_name = '{}:{}'.format(self._list_name, entry.id)
        hash_dict = {}
        field_names = list(entry.__all__)
        field_names.remove('id')
        for field_name in field_names:
            hash_dict[field_name] = getattr(entry, field_name)

        self._pipeline.hmset(hash_name, hash_dict)

    def flush_buffer(self):
        """
        Flush the pipeline (Redis' buffer) to Redis.
        """
        if self._pipeline:
            self._pipeline.execute()

    def iterate(self):
        """
        Iterate over the Redis list.
        Return an iterator object which iterates over `Redis<Provider>Entry` objects.
        """
        r = open_redis_connection()
        pipeline = r.pipeline()

        def _lpop():
            """
            Pop from the head of the Redis list and get the hash entry.
            Convert the pop and hash items to a `Redis<Provider>Entry` instance.
            """
            entry_id = r.lpop(self._list_name)
            if not entry_id:  # The list has been completely consumed.
                return None

            hash_name = '{}:{}'.format(self._list_name, entry_id.decode(encoding='UTF-8'))
            entry_dict = r.hgetall(hash_name)
            # Delete the hash through a pipeline. The use of a pipeline is to avoid a sort
            # of bug. The bug was the following:
            # entry = r.hgetall(hash_name)  -- READ
            # r.delete(hash_name)           -- DELETE
            # Sometimes the DELETE happens before the READ causing the read value to be None: this
            # is very very weird, but it happened sometimes. Using a pipeline solve this.
            pipeline.delete(hash_name)
            return self._init_redis_provider_entry(entry_id, entry_dict)

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

    @staticmethod
    @abstractmethod
    def _init_redis_provider_entry(*args, **kwargs):
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
            setattr(self, field_name, entry_dict[field_name.encode()].decode('UTF-8'))

        self._sanity_check()

    def _sanity_check(self):
        pass