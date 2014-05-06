from .crawler import DropboxCrawler
from .downloader import DropboxDownloader
from .indexer import DropboxIndexer
from synchronizer import AbstractSynchronizer


class DropboxSynchronizer(AbstractSynchronizer):
    """
    Manage the synchronization with Dropbox.
    """
    def run(self):
        print(">>>>>> START CRAWLING")
        # `DropboxCrawler` receives a `BearerToken` argument because it needs to update
        # its cursor.
        DropboxCrawler(self.bearertoken).run()
        print(">>>>>> END CRAWLING")

        # `DropboxDownloader` parameters are the bearertoken id and access_token. A proper
        # `BearerToken` instance is not required because no update is required.
        # Plus passing `self.bearertoken` would have resulted in an edited object in SQLAlchemy
        # session, because it was edited (and committed) by `DropboxCrawler`.
        print("\n\n>>>>>> START DOWNLOADING")
        DropboxDownloader(self._bearertoken_id, self._access_token).run()
        print(">>>>>> END DOWNLOADING")

        print("\n\n>>>>>> START INDEXING")
        DropboxIndexer(self._bearertoken_id, self._access_token).run()
        print(">>>>>> END INDEXING")