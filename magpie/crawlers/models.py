import os

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from .exceptions import ImproperlyConfigured

Base = declarative_base()



from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncodedDict(TypeDecorator):
    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)

    """

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value, indent=4)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value




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
    scope = Column(JSONEncodedDict(1024))

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
    access_token = Column(JSONEncodedDict(1024))

    # TODO so far I don't need a User
    #user = ... foreign key to a User table
    #unique_together = ("user", "provider")




