from dropbox.client import DropboxClient  # Dropobox official library

from ..dbutils import session_autocommit
from .response import DropboxResponse


class DropboxCrawler:
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    @property
    def _client(self):
        """
        A `dropbox.DropboxClient` for the current `bearertoken`.
        It is a cached attribute so that it is a singleton.
        """
        try:
            cl = self._client_cached
        except AttributeError:
            cl = self._client_cached = DropboxClient(self.bearertoken.access_token)
        return cl

    def run(self):
        """
        Crawl Dropbox for updates and write en entry for each item to Redis.
        """
        # When crawling Dropbox, the response contains max about 1000 items plus a has_more flag.
        # We have to keep repeating the crawling until has_more is false.
        # For each crawl we open a new session, such as, in case of failure of a single crawl, only
        # that specific crawl is rolled back.
        # Bare in mind that in the 99% of cases there is only 1 crawl because users usually
        # don't update more than 1000 files in the time in between 2 syncs.
        while True:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                self.bearertoken = sex.merge(self.bearertoken)

                # TODO Catch the exception dropbox.rest.ErrorResponse: [401] "The given OAuth 2
                # TODO access token doesn't exist or has expired."
                r = self._client.delta(cursor=self.bearertoken.updates_cursor,
                                       path_prefix='/temp/moogletest')  # TODO remove the prefix

                # Parse the response.
                response = DropboxResponse(r)
                response.parse(self.bearertoken.id)

                # Update the cursor.
                self.bearertoken.updates_cursor = response.updates_cursor

                # Continue only in case Dropbox `has_more` items to send.
                if response.has_more:
                    continue
                break
