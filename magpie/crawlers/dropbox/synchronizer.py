from .crawler import DropboxCrawler
from .downloader import DropboxDownloader


class DropboxSynchronizer:
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    def run(self):

        # TODO temporary reset the cursor for debugging purpose only
        from ..dbutils import session_autocommit
        with session_autocommit() as sex:
            self.bearertoken.updates_cursor = None

        DropboxCrawler(self.bearertoken).run()

        DropboxDownloader(self.bearertoken).run()

        #DropboxIndexer(self.bearertoken).run()
        # gets all the entries in redis with this bearertoken_id
        # process them according to the order defined by seq_n
        # for each +, tells solr to index the local file
        # for each -, deletes the record from Solr (name and name/*)




