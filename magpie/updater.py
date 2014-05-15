from abc import ABCMeta, abstractmethod

from utils.db import session_autocommit
from models import BearerToken, Provider


class AbstractUpdater(metaclass=ABCMeta):
    """
    Fetch updates from a Provider for a `bearertoken`.

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


class UpdateManager:
    """
    Launch updates for a `bearertoken_id`.

    Parameters:
    bearertoken_id -- the id of the `BearerToken` whose updates we will fetch.
    """
    # Imports here to avoid circular imports.
    from twitterlib.updater import TwitterUpdater
    from facebooklib.updater import FacebookUpdater
    from dropboxlib.updater import DropboxUpdater

    updaters_class_names = {
        Provider.NAME_TWITTER: TwitterUpdater,
        Provider.NAME_FACEBOOK: FacebookUpdater,
        Provider.NAME_DROPBOX: DropboxUpdater,
    }

    def __init__(self, bearertoken_id):
        with session_autocommit() as sex:
            self.bearertoken = sex.query(BearerToken).filter_by(id=bearertoken_id).one()
            self.provider_name = self.bearertoken.provider.name

    @abstractmethod
    def run(self):
        updater = self.updaters_class_names[self.provider_name](self.bearertoken)
        updater.run()