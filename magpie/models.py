import os
import json

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from utils.exceptions import ImproperlyConfigured


Base = declarative_base()


class Provider(Base):
    __tablename__ = "crawlers.provider"

    id = Column(Integer, primary_key=True)
    NAME_DRIVE = 'drive'
    NAME_GMAIL = 'gmail'
    NAME_FACEBOOK = 'facebook'
    NAME_TWITTER = 'twitter'
    NAME_DROPBOX = 'dropbox'
    NAME_CHOICES = (NAME_DRIVE, NAME_GMAIL, NAME_FACEBOOK, NAME_TWITTER, NAME_DROPBOX)
    name = Column(Enum(*NAME_CHOICES))
    redirect_url = Column(String(200), nullable=False)
    authorization_base_url = Column(String(256), nullable=False)
    token_url = Column(String(256), nullable=False)
    request_token_url = Column(String(256), nullable=False)
    oauth_version = Column(String(5))
    _scope = Column(String(1024))

    # `_scope` is json text containing a serialized list like:
    # ["https://www.googleapis.com/auth/userinfo.email", "https://mail.google.com"]
    # A getter and a setter property are defined on this field to automatize the conversion
    # from json text to python  objects.
    #
    # I tried to use a custom type from SQLAlchemy in order to manage JSON text, following this:
    # http://docs.sqlalchemy.org/en/rel_0_9/core/types.html#marshal-json-strings
    # But it didn't work out:
    #  - the method `process_bind_param` was correctly called before saving to db
    #  - but the method `process_result_value` was never called when reading from db
    # Anyway this Python-level solution is always great and reliable.
    @property
    def scope(self):
        """
        Getter property for _scope to automatize the conversion from json text to python objects.
        Read a json string from the db and return a python dictionary.
        """
        try:
            return json.loads(self._scope)
        except ValueError:
            return None

    @scope.setter
    def scope(self, value):
        """
        Setter property for _scope to automatize the conversion from json text to python objects.
        Receive a python dictionary and store a json string to the db.
        """
        self._scope = json.dumps(value, indent=4)

    @property
    def client_id(self):
        """
        Getter property for <PROVIDER_NAME>_CLIENT_ID environment variable.
        """
        try:
            var_name = "{}_CLIENT_ID".format(self.name.upper())
            return os.environ[var_name]
        except KeyError:
            msg = "You must set the environment variable: {}".format(var_name)
            raise ImproperlyConfigured(msg)

    @property
    def client_secret(self):
        """
        Getter property for <PROVIDER_NAME>_CLIENT_SECRET environment variable.
        """
        try:
            var_name = "{}_CLIENT_SECRET".format(self.name.upper())
            return os.environ[var_name]
        except KeyError:
            msg = "You must set the environment variable: {}".format(var_name)
            raise ImproperlyConfigured(msg)

    def __repr__(self):
        return "<Provider(id={}, name={}>".format(self.id, self.name)


class BearerToken(Base):
    __tablename__ = "crawlers.bearertoken"

    id = Column(Integer, primary_key=True)
    # Set the related field on the other table (provider.id)
    provider_id = Column(Integer, ForeignKey('crawlers.provider.id'))
    # Set the other table (Provider) and the name of the reverse relationship (bearertokens)
    provider = relationship("Provider", backref=backref('bearertokens'))
    # `updates_cursor` is the cursor used to keep track of the position of the last update.
    # Using a cursor during an update lets us get only the updates happened after the previous
    # update. The cursor is text and it has different forms for different providers.
    # E.g. for Dropbox: AAFkqARCY6KnIayYJYqpcIP0-HMWsc4vf21aWJ...RMM1S2V0UoP3Ui_AXIJxtASbBuxveOuKw
    updates_cursor = Column(String(512))
    _token_set = Column(String(1024))

    # TODO so far I don't need a User
    #user = ... foreign key to a User table
    #unique_together = ("user", "provider")

    # `_token_set` is json text containing a serialized dictionary like:
    #{
    #    "refresh_token": "1/RPFj6FA6UahmuPUj3NqDEhdvfYNnXHCSIvhm1d2Yoj0",
    #    "expires_in": 3600,
    #    "token_type": "Bearer",
    #    "access_token": "ya29.1.AADtN_VwezbeOQGkJE4_3ZDNZimrRf86Dn...pL8YB1rpVRhav0-mIiHEmV8",
    #    "id_token": "eyJhbGciOiJSUzI1NiIsI...U3MWJlNZoempIreV572mbxH7Rm90eNQwfShPQnI49u8bZgc"
    #}
    # This example is a OAuth2 token (from Google) but it can be also OAuth1 token (like Twitter)
    # A getter and a setter property are defined on this field to automatize the conversion
    # from json text to python  objects.
    #
    # Getter and setter properties for _token_set to automatize the conversion from json text
    # to python objects.
    # The getter reads a json string from the db and returns a python dictionary.
    @property
    def token_set(self):
        """
        Getter property for `_token_set` to automatize the conversion from json text to python
        objects. Read a json string from the db and return a python dictionary.
        """
        try:
            return json.loads(self._token_set)
        except ValueError:
            return None

    @token_set.setter
    def token_set(self, value):
        """
        Setter property for `_token_set` to automatize the conversion from json text to python
        objects. Receive a python dictionary and store a json string to the db.
        """
        self._token_set = json.dumps(value, indent=4)

    @property
    def access_token(self):
        """
        Getter property for the access_token stored in `token_set` dictionary.
        """
        return self.token_set.get('access_token', '')

    @access_token.setter
    def access_token(self, value):
        raise NotImplementedError("You can NOT set access_token. Use token_set instead.")

    @property
    def oauth_token(self):
        """
        Getter property for the oauth_token stored in `token_set` dictionary.
        Used by OAuth 1.0a (Twitter).
        """
        return self.token_set.get('oauth_token', '')

    @oauth_token.setter
    def oauth_token(self, value):
        raise NotImplementedError("You can NOT set oauth_token. Use token_set instead.")

    @property
    def oauth_token_secret(self):
        """
        Getter property for the oauth_token_secret stored in `token_set` dictionary.
        Used by OAuth 1.0a (Twitter).
        """
        return self.token_set.get('oauth_token_secret', '')

    @oauth_token_secret.setter
    def oauth_token_secret(self, value):
        raise NotImplementedError("You can NOT set oauth_token_secret. Use token_set instead.")

    @property
    def user_id(self):
        """
        Getter property for the user_id stored in `token_set` dictionary.
        Used by OAuth 1.0a (Twitter).
        """
        return self.token_set.get('user_id', '')

    @user_id.setter
    def user_id(self, value):
        raise NotImplementedError("You can NOT set user_id. Use token_set instead.")

    def __repr__(self):
        provider_name = self.provider.name if self.provider else ''
        return "<BearerToken(id={}, provider={})>".format(self.id, provider_name)




