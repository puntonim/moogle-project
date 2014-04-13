from dropbox.client import DropboxClient  # Dropobox official library

from ..dbutils import session_autocommit
from magpie.settings import settings
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

        # TODO now we read it from file but they should be in Redis
        from os.path import normpath, join
        TMP_REDIS_FILE = normpath(join(settings.DROPBOX_TEMP_REPO_PATH, '{}.txt'.format(
            self.bearertoken_id)))
        for line in open(TMP_REDIS_FILE):
            _, path, operation = line.split('\t')

            # Bare in mind that:
            # + > they are only files (no dir because they have been filtered out previously)
            # - > we don't know if they are files or dir but we don;t care since we delete:
            #     name and name/*

            # If the record is a - skip it

            # If the record is a + and has no local_path field:
            #   download the file
            #   add local_path field

            # Download the file. We could use client.get_file or client.get_file_and_metadata,
            # but under the hood the actual call to the API is the same, cause that basic API
            # call returns the file plus its metadata.
            content, metadata = self._client.get_file_and_metadata(path)
            file = DropboxFile(content, metadata)
            file.store_to_disk(self.bearertoken_id)