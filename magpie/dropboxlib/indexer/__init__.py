import logging

from ..redislist import RedisDropboxIndexList
from .solrupdater import DropboxSolrUpdater


log = logging.getLogger('dropbox')


class DropboxIndexer:
    """
    ...
    """

    def __init__(self, bearertoken_id, access_token):
        self.bearertoken_id = bearertoken_id
        self.access_token = access_token

    def run(self):
        redis = RedisDropboxIndexList(self.bearertoken_id)
        solr = DropboxSolrUpdater(self.bearertoken_id)
        for redis_entry in redis.iterate():
            # `redis_entry` is a `RedisDropboxEntry` instance.

            # If:
            #   - `redis_entry.is_del()`: delete the file from Sorl
            #   - `redis_entry.is_reset()`: delete the entire index from Solr
            #   - `redis_entry.is_add()`: add the file to Solr (the file has already
            #     been downloaded locally)
            #
            # Bear in mind that:
            #   - entries with `redis_entry.is_add()` are only files (no dirs cause they have
            #     already been filtered out)
            #   - entries with `redis_entry.is_del()`: we don't know if they are files or dir
            #     but we don't care since during indexing we ask Solr to delete: name and name/*
            # And a sanity check is run when creating a `RedisDropboxEntry` instance.

            if redis_entry.is_del():
                log.debug('DEL: {}'.format(redis_entry.remote_path))
                solr.delete(redis_entry)

            if redis_entry.is_reset():
                log.debug('RESET')
                solr.reset()

            if redis_entry.is_add():
                log.debug('ADD: {}'.format(redis_entry.remote_path))
                solr.add(redis_entry)
        solr.commit()