from abc import ABCMeta, abstractmethod

from utils.db import session_autocommit


class AbstractCrawler(metaclass=ABCMeta):
    """
    Web crawler to query a service `Provider` and collect posts for a `bearertoken`.

    Parameters:
    bearertoken -- a `models.BearerToken`
    """
    def __init__(self, bearertoken):
        self.bearertoken = bearertoken

    @property
    def _client(self):
        """
        A `OAuth1Session` for the current `bearertoken`.
        It is a cached attribute so that it is a singleton.
        """
        try:
            cl = self._client_cached
        except AttributeError:
            cl = self._client_cached = self._init_client()
        return cl

    @abstractmethod
    def _init_client(self):
        pass

    @staticmethod
    @abstractmethod
    def _init_response(*args, **kwargs):
        pass

    def run(self):
        """
        Crawl Facebook for new posts and write en entry for each item to Redis.
        """
        is_first_loop = True  # for pagination.
        pagination_cursor = ''  # for pagination.
        while True:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                self.bearertoken = sex.merge(self.bearertoken)

                resource_url = self._build_resource_url(pagination_cursor)

                # Perform the query.
                # Note: the correctness of the response is checked when creating
                # the response with _init_response().
                r = self._client.get(resource_url)

                # Parse the response.
                response = self._init_response(r)
                response.parse(self.bearertoken.id)

                self._hook_after_response_parsed(response)

                # Pagination.
                if is_first_loop:
                    updates_cursor = response.updates_cursor
                    is_first_loop = False

                # Continue only in case the response `has_more` items to query.
                if response.has_more:
                    if hasattr(response, 'pagination_cursor'):
                        pagination_cursor = response.pagination_cursor
                    continue
                break

        # Update the updates_cursor only at the end, when everything has been successfully
        # completed.
        self._update_updates_cursor(updates_cursor)

    @abstractmethod
    def _build_resource_url(self, pagination_cursor):
        pass

    def _hook_after_response_parsed(self, response):
        pass

    def _update_updates_cursor(self, new_updates_cursor):
        """
        Update the updates_cursor parameter on the database.
        """
        if new_updates_cursor:
            with session_autocommit() as sex:
                # Add bearertoken to the current session.
                bearertoken = sex.merge(self.bearertoken)

                bearertoken.updates_cursor = new_updates_cursor
