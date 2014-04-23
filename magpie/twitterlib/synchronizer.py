from .crawler import TwitterCrawler
from .indexer import TwitterIndexer
from utils.db import session_autocommit


class TwitterSynchronizer:
    """

    Parameters:
    bearertoken -- a `BearerToken` owner of the owner of the Twitter account to synchronize with.
    """
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken
        with session_autocommit() as sex:
            # Add bearertoken to the current session.
            bearertoken = sex.merge(self.bearertoken)
            self._bearertoken_id = bearertoken.id
            self._access_token = bearertoken.access_token

    def run(self):

        # TODO temporary reset the cursor for debugging purpose only
        self._TMP_reset_cursor()

        print(">>>>>> START CRAWLING")
        # `DropboxCrawler` receives a `BearerToken` argument because it needs to update
        # its cursor.
        TwitterCrawler(self.bearertoken).run()
        print(">>>>>> END CRAWLING")

        print("\n\n>>>>>> START INDEXING")
        TwitterIndexer(self._bearertoken_id, self._access_token).run()
        print(">>>>>> END INDEXING")



    # TODO delete me
    def _TMP_reset_cursor(self):
        from utils.db import session_autocommit
        with session_autocommit() as sex:
            self.bearertoken.updates_cursor = None
