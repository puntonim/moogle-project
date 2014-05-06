from .crawler import FacebookCrawler
from .indexer import FacebookIndexer
from synchronizer import AbstractSynchronizer


class FacebookSynchronizer(AbstractSynchronizer):
    """
    Manage the synchronization with Facebook.
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
