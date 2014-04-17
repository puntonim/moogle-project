from dropbox.client import DropboxClient  # Dropobox official library

from ..dbutils import session_autocommit
from ..redisutils import RedisStore
from ..exceptions import RedisDownloadEntryInconsistentError
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
        """

        """
        print("Downloading for bearerid: ", self.bearertoken_id)

        redis_store = RedisStore(self.bearertoken_id)
        for redis_dw_entry in redis_store.iter_over_download_list():
            # `redis_dw_entry` is a `RedisDownloadEntry` instance.

            # If:
            #   - `redis_dw_entry.operation` is '-': move the entry to the index list
            #   - `redis_dw_entry.operation` is 'X' and `redis_dw_entry.remote_path` is 'RESET':
            #     move the entry to the index list
            #   - `redis_dw_entry.operation` is '+': download the file locally, update
            #     `redis_dw_entry.remote_path` with the local file name, move the entry to the
            #     index list
            #
            # Bear in mind that:
            # '+': they are only files (no dirs cause they have already been filtered out)
            # '-': we don't know if they are files or dir but we don't care since during
            #      indexing we ask Solr to delete: name and name/*

            # TODO
            print(redis_dw_entry.operation_type, redis_dw_entry.remote_path)
            self._sanity_check(redis_dw_entry)

            if redis_dw_entry.operation_type == '+':
                # Download the file. We could use client.get_file or client.get_file_and_metadata,
                # but under the hood the actual call to the API is the same, cause that basic API
                # call returns the file plus its metadata.
                content, metadata = self._client.get_file_and_metadata(redis_dw_entry.remote_path)
                file = DropboxFile(content, metadata)
                file.store_to_disk(self.bearertoken_id)
                # Update `remote_path` attribute with the local name
                redis_dw_entry.remote_path = file.local_name

            redis_store.add_to_index_list_buffer(redis_dw_entry)
        redis_store.flush_index_list_buffer()

    @staticmethod
    def _sanity_check(redis_dw_entry):
        """
        `redis_dw_entry` is a `RedisDownloadEntry` instance.
        Valid values for `operation` attribute are: '+', '-', 'X'.
        If the `operation` is 'X' the `remote_path` must be 'RESET'.
        """
        if not redis_dw_entry.operation_type in ['+', '-', 'X']:
            raise RedisDownloadEntryInconsistentError("The operation must be '+', '-' or 'X'.")

        if redis_dw_entry.operation_type == 'X' and not redis_dw_entry.remote_path == 'RESET':
            raise RedisDownloadEntryInconsistentError("If the operation is 'X' the remote_path"
                                                      "must be 'REST'.")