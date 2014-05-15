from .crawler import TwitterCrawler
from .indexer import TwitterIndexer
from updater import AbstractUpdater


class TwitterUpdater(AbstractUpdater):
    """
    Fetch updates from Twitter for a `bearertoken`.
    """
    def run(self):
        print(">>>>>> START CRAWLING")
        # `DropboxCrawler` receives a `BearerToken` argument because it needs to update
        # its cursor.
        TwitterCrawler(self.bearertoken).run()
        print(">>>>>> END CRAWLING")

        print("\n\n>>>>>> START INDEXING")
        TwitterIndexer(self._bearertoken_id, self._access_token).run()
        print(">>>>>> END INDEXING")
