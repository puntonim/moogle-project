from .crawler import DropboxCrawler


class DropboxSynchronizer:
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    def run(self):
        DropboxCrawler(self.bearertoken).run()

        #DropboxDownloader(self.bearertoken).run()

        #DropboxIndexer(self.bearertoken).run()





