import datetime
from unittest.mock import Mock

from redislist import AbstractRedisList
from .entry import RedisDropboxEntry, AbstractDropboxEntry


class RedisDropboxDownloadList(AbstractRedisList):
    """
    A Redis list which maps Dropbox files.
    Entries of the list in Redis have this form: "+/dir1/file2.txt".
    The first char can be:
      '+' if it is a file to download
      '-' if it is a file to delete
    'XRESET' means that the entire Dropbox root folder must be deleted.
    """
    @staticmethod
    def _build_list_name(bearertoken_id):
        return 'dropbox:dw:token:{}'.format(bearertoken_id)

    @staticmethod
    def _init_redis_provider_entry(*args, **kwargs):
        return RedisDropboxEntry(*args, **kwargs)

    def buffer_add_reset(self):
        """
        Add a reset instruction to Redis' download list (through a pipeline which is a buffer).
        """
        entry = Mock()
        entry.__all__ = AbstractDropboxEntry.__all__
        epoch = datetime.datetime.utcfromtimestamp(0)
        now = datetime.datetime.now()
        entry.id = '{}'.format((now - epoch).total_seconds())  # Seconds.milliseconds from epoch.
        entry.remote_path = 'RESET'
        entry.local_name = 'RESET'
        entry.operation = 'X'
        self.buffer(entry)


class RedisDropboxIndexList(AbstractRedisList):
    """
    A Redis list which maps files to index with Solr.
    Entries of the list in Redis have this form: "+/dir1/file2.txt".
    The first char can be:
      '+' if it is a file already downloaded locally and ready to be indexed
      '-' if it is a file to delete from the index
    'XRESET' means that the entire index must be deleted.
    """
    @staticmethod
    def _build_list_name(bearertoken_id):
        return 'dropbox:ix:token:{}'.format(bearertoken_id)

    @staticmethod
    def _init_redis_provider_entry(*args, **kwargs):
        return RedisDropboxEntry(*args, **kwargs)