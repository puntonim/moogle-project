from .crawler import DropboxCrawler
from .downloader import DropboxDownloader
from ..dbutils import session_autocommit


class DropboxSynchronizer:
    """

    Parameters:
    bearertoken -- a `BearerToken` owner of the owner of the Dropbox account to synchronize with.
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
        # `DropboxCrawler` parameter is a `BearerToken` instance because it needs to update its
        # cursor.
        DropboxCrawler(self.bearertoken).run()
        print(">>>>>> END CRAWLING")

        print(">>>>>> START DOWNLOADING")
        # `DropboxDownloader` parameters are the bearertoken id and access_token. A proper
        # `BearerToken` instance is not required because no update is required.
        # Plus passing `self.bearertoken` would have resulted in an edited object in SQLAlchemy
        # session, because it was edited (and committed) by `DropboxCrawler`.
        DropboxDownloader(self._bearertoken_id, self._access_token).run()
        print(">>>>>> END DOWNLOADING")

        #DropboxIndexer(self.bearertoken).run()
        # gets all the entries in redis with this bearertoken_id
        # process them according to the order defined by seq_n
        # for each +, tells solr to index the local file
        # for each -, deletes the record from Solr (name and name/*)



    # TODO delete me
    def _TMP_reset_cursor(self):
        from ..dbutils import session_autocommit
        with session_autocommit() as sex:
            self.bearertoken.updates_cursor = None