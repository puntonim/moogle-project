from utils.exceptions import TwitterResponseError
from .responseentry import TwitterResponseEntry
from ..redis import RedisTwitterList


class TwitterResponse:
    """

    Parameters:
    response -- a `requests.models.Response` instance.
    """

    def __init__(self, response):
        self.response = response
        self.updates_cursor = ''
        self.max_id = ''
        self.has_more = False

        self._sanity_check()

    def parse(self, bearertoken_id):
        redis = RedisTwitterList(bearertoken_id)

        is_first_entry = True
        for entry in self._entries_to_twitterresponseentries():
            # `entry` is a `TwitterResponseEntry` instance.

            #print(entry.entry_dict['text'])
            redis.buffer(entry)

            # Pagination
            # We suppose that if there is at least an entry in this response, then the response
            # is not complete and a new query should be run (this is not exactly true, but it
            # works since it stops when the response has no entry).
            self.has_more = True
            if is_first_entry:
                self.updates_cursor = entry.id_str
                is_first_entry = False
            self.max_id = str(int(entry.id_str) - 1)

        redis.flush_buffer()

    def _entries_to_twitterresponseentries(self):
        """
        Iter over all entries in the response.
        `entries` is a list of items; each item is converted to a `DropboxResponseEntry` instance.
        """

        rj = self.response.json()

        def _lpop():
            """
            Pop from the head of the list.
            Convert the item to `DropboxResponseEntry`.
            """
            while True:
                try:
                    entry = rj.pop(0)
                    entry = TwitterResponseEntry(entry)
                    return entry
                except IndexError:
                    # `self.response` is empty, return None to stop the iter
                    return None
                #except EntryNotToBeIndexed:
                    # The entry is probably a dir or not a textual file and we don't need to
                    # index it
                #    continue
                #except InconsistentItemError as e:
                    # The entry is not consistent, like some important metadata are missing,
                    # we just skip it
                    # TODO log it anyway
                #    continue

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)

    def _sanity_check(self):
        """
        Check whether the current response got from Twitter is an error response.
        """
        if self.response.status_code != 200:
            # If the HTTP status code is not 200, then it is an error
            msg = 'HTTP Status: {}\n{}'.format(self.response.status_code, self.response.json())
            raise TwitterResponseError(msg)
        # TODO implement a check on rate limit error (max 180 GET requests per access_token
        # TODO every 15 min): https://dev.twitter.com/docs/rate-limiting/1.1/limits
