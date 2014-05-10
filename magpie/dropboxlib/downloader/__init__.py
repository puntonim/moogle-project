import logging
from dropbox.client import DropboxClient  # Dropobox official library

from ..redislist import RedisDropboxDownloadList, RedisDropboxIndexList
from .dropboxfile import DropboxFile


log = logging.getLogger('dropbox')


class DropboxDownloader:
    """
    Download files from Dropbox based on a list previously built by the `DropboxCrawler` and
    stored internally.

    Parameters:
    bearertoken_id -- the id of the `BearToken` owner of the Dropbox account.
    access_token -- the access token of the `BearToken` owner of the Dropbox account.
    """

    def __init__(self, bearertoken_id, access_token):
        self.bearertoken_id = bearertoken_id
        self.access_token = access_token

    @property
    def _client(self):
        """
        A `dropbox.DropboxClient` for the current `bearertoken`.
        It is a cached attribute so that it is a singleton.
        """
        try:
            cl = self._client_cached
        except AttributeError:
            cl = self._client_cached = DropboxClient(self.access_token)
        return cl

    def run(self):
        print("Downloading for bearerid: ", self.bearertoken_id)

        redis_dw = RedisDropboxDownloadList(self.bearertoken_id)
        redis_ix = RedisDropboxIndexList(self.bearertoken_id)
        for redis_entry in redis_dw.iterate():
            # `redis_entry` is a `RedisDropboxEntry` instance.

            # If:
            #   - `redis_entry.is_del()`: move the entry to the index list
            #   - `redis_entry.is_reset()`: move the entry to the index list
            #   - `redis_entry.is_add()`: download the file locally, update
            #     `redis_entry.remote_path` with the local file name, move the entry to the
            #     index list
            #
            # Bear in mind that:
            #   - entries with `redis_entry.is_add()` are only files (no dirs cause they have
            #     already been filtered out)
            #   - entries with `redis_entry.is_del()`: we don't know if they are files or dir
            #     but we don't care since during indexing we ask Solr to delete: name and name/*
            # And a sanity check is run when creating a `RedisDropboxEntry` instance.

            # TODO
            print(redis_entry.operation, redis_entry.remote_path)

            if redis_entry.is_add():
                # Download the file. We could use client.get_file or client.get_file_and_metadata,
                # but under the hood the actual call to the API is the same, cause that basic API
                # call returns the file plus its metadata.
                log.debug('Downloading: {}'.format(redis_entry.remote_path))
                content, metadata = self._client.get_file_and_metadata(redis_entry.remote_path)
                file = DropboxFile(content, metadata)
                file.store_to_disk(self.bearertoken_id)
                # Update `remote_path` attribute with the local name
                redis_entry.local_name = file.local_name

            redis_ix.buffer(redis_entry)
        redis_ix.flush_buffer()