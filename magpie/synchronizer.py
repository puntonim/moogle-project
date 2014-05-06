from abc import ABCMeta, abstractmethod

from utils.db import session_autocommit


class AbstractSynchronizer(metaclass=ABCMeta):
    """
    Manage the synchronization with `Provider`s.

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

    @abstractmethod
    def run(self):
        pass