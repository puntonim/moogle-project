from .crawler import DropboxCrawler
from .downloader import DropboxDownloader


class DropboxSynchronizer:
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    def run(self):
        DropboxCrawler(self.bearertoken).run()

        #DropboxDownloader(self.bearertoken).run()
        # gets all entries in redis w/ this bearertoken
        # for each + with no local_path filed, downloads the file, updateds the local_path field
        # w the local filepath

        #DropboxIndexer(self.bearertoken).run()
        # gets all the entries in redis with this bearertoken_id
        # process them according to the order defined by seq_n
        # for each +, tells solr to index the local file
        # for each -, deletes the record from Solr (name and name/*)




