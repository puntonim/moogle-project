from dropbox.client import DropboxClient  # Dropobox official library

from ..dbutils import session_autocommit
from ..redisutils import RedisStore
from .file import DropboxFile


class DropboxDownloader:
    """
    Download files from Dropbox based on a list previously built by the `DropboxCrawler` and
    stored internally.

    Parameters:
    bearertoken -- the beartoken owner of the Dropbox account. This bearertoken
    """

    def __init__(self, bearertoken):
        with session_autocommit() as sex:
            # Add bearertoken to the current session.
            bearertoken = sex.merge(bearertoken)
            self.bearertoken_id = bearertoken.id
            self.access_token = bearertoken.access_token

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
        print("mo scarico per", self.bearertoken_id)


        # Gets all entries in redis dw list
        # for each +: downloads the file and add an entry to redis ix list (w local file name)
        # for each -: adds an entry to redis ix list
        # Bear in mind that:
        # + are only files (no dirs cause they have already been filtered out)
        # - are we don't know if they are files or dir but we don't care since during
        # indexing we ask solr to delete: name and name/*

        redis_store = RedisStore(self.bearertoken_id)
        for redis_dw_entry in redis_store.iter_over_download_list():

            print(redis_dw_entry.operation_type, redis_dw_entry.remote_path)

            # TODO finish this


            # Download the file. We could use client.get_file or client.get_file_and_metadata,
            # but under the hood the actual call to the API is the same, cause that basic API
            # call returns the file plus its metadata.
            #content, metadata = self._client.get_file_and_metadata(path)
            #file = DropboxFile(content, metadata)
            #file.store_to_disk(self.bearertoken_id)
