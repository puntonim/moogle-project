from abc import ABCMeta, abstractmethod

from utils.exceptions import ResponseError, InconsistentItemError, EntryNotToBeIndexed


class AbstractApiResponse(metaclass=ABCMeta):
    """
    Response got after a query to a `Provider`.

    Parameters:
    response -- a `requests.models.Response` instance.
    """

    def __init__(self, response):
        self.response = response
        self.updates_cursor = ''
        self.has_more = False
        self.pagination_cursor = ''

        self._sanity_check()

    def _sanity_check(self):
        """
        Check whether the current response got is an error response.
        """
        # If the HTTP status code is not 200, then it is an error.
        if self.response.status_code != 200:
            msg = 'HTTP Status: {}\n{}'.format(self.response.status_code, self.response.json())
            raise ResponseError(msg)

    def parse(self, bearertoken_id):
        redis = self._init_redis_list(bearertoken_id)

        self._hook_parse_entire_response(redis)

        is_first_entry = True
        entry = None
        for entry in self._entries_to_apientries():
            # `entry` is a `Api<Provider>Entry` instance.

            redis.buffer(entry)

            # Updates cursor: the `updated_time` of the most recent post.
            if is_first_entry:
                self._hook_parse_first_entry(entry)
                is_first_entry = False

        if entry:  # if there is any `entry`
            self._hook_parse_last_entry(entry)

        redis.flush_buffer()

    @abstractmethod
    def _init_redis_list(self, *args, **kwargs):
        pass

    def _hook_parse_entire_response(self, redis):
        pass

    def _hook_parse_first_entry(self, entry):
        pass

    def _hook_parse_last_entry(self, entry):
        pass

    @abstractmethod
    def _build_pagination_cursor(self):
        pass

    @abstractmethod
    def _build_updates_cursor(self):
        pass

    def _entries_to_apientries(self):
        """
        Iter over all entries in the response.
        Each entry in the response is converted to a `Api<Provider>Entry` instance.
        """

        entries_list = self._extract_entries_list()

        def _lpop():
            """
            Pop from the head of the list.
            Convert the item to `Api<Provider>Entry`.
            """
            while True:
                try:
                    entry = entries_list.pop(0)  # Raise IndexError when completely consumed.
                    entry = self._init_api_provider_entry(entry)
                    return entry
                except IndexError:
                    # `self.response` is empty, return None to stop the iter.
                    return None
                except EntryNotToBeIndexed:
                    # The entry is probably a dir or not a textual file and we don't need to
                    # index it
                    continue
                except InconsistentItemError as e:
                    # The entry is not consistent, like some important metadata are missing,
                    # we just skip it
                    # TODO log it anyway
                    continue

        # The first argument of iter must be a callable, that's why we created the _lpop()
        # closure. This closure will be called for each iteration and the result is returned
        # until the result is None.
        return iter(_lpop, None)

    def _extract_entries_list(self):
        return self.response.json()

    @abstractmethod
    def _init_api_provider_entry(self, *args, **kwargs):
        pass