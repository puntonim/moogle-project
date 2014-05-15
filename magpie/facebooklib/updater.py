from .crawler import FacebookCrawler
from .indexer import FacebookIndexer
from updater import AbstractUpdater


class FacebookUpdater(AbstractUpdater):
    """
    Fetch updates from Facebook for a `bearertoken`.
    """
    def run(self):
        print(">>>>>> START CRAWLING")
        # `FacebookCrawler` receives a `BearerToken` argument because it needs to update
        # its cursor.
        FacebookCrawler(self.bearertoken).run()
        print(">>>>>> END CRAWLING")

        print("\n\n>>>>>> START INDEXING")
        FacebookIndexer(self._bearertoken_id, self._access_token).run()
        print(">>>>>> END INDEXING")
