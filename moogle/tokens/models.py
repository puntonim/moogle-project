import os
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.contrib.auth.models import User
import json
from .managers import BearerTokenManager


class Provider(models.Model):
    """
    A resource provider like Facebook, Google Drive, Twitter, ...
    It provides OAuth 2.0 protected resources.
    Any bearer (like Moogle) can access its protected resources using bearer tokens.
    """

    # `name` is a choice field because we only allow a pre-defined set of providers to be added.
    # Ideally each provider should have been a model, like FacebookProvider, TwitterProvider, ...
    # but they are all alike, no difference at all, so we decided to use only a model.
    # The choice field is made of a machine-friendly name
    # We could have added a `name_verbose` field for a descriptive user-friendly name but we
    # decided that the choice field can handle this. Descriptive names never change so we don't
    # see the point in adding a new filed to the database.
    # Machine-friendly names, only lowercase and - (no space)
    NAME_DRIVE = 'drive'
    NAME_GMAIL = 'gmail'
    NAME_FACEBOOK = 'facebook'
    NAME_TWITTER = 'twitter'
    NAME_DROPBOX = 'dropbox'
    # Now build `NAME_CHOICES` with tuples made of:
    #  (machine-friendly name, user-friendly name)
    NAME_CHOICES = (
        (NAME_DRIVE, 'Google Drive'),
        (NAME_GMAIL, 'Google Gmail'),
        (NAME_FACEBOOK, 'Facebook'),
        (NAME_TWITTER, 'Twitter'),
        (NAME_DROPBOX, 'Dropbox'),
    )
    # For `name` choice field:
    # provider.name returns the machine-friendly name
    # provider.get_name_display() returns the user-friendly name
    name = models.CharField(max_length=20, choices=NAME_CHOICES, unique=True)
    redirect_url = models.CharField(max_length=200)  # Relative url, f.i.: /oauth/google/callback
    authorization_base_url = models.URLField()
    token_url = models.URLField()
    request_token_url = models.URLField(blank=True)  # Used only in Oauth1
    oauth_version = models.CharField(max_length=5, blank=True)  # e.g. 2 or 1.0a
    # `_scope` is json text containing a serialized list like:
    # ["https://www.googleapis.com/auth/userinfo.email", "https://mail.google.com"]
    # A getter and a setter property are defined on this field to automatize the conversion
    # from json text to python  objects.
    _scope = models.TextField(blank=True)  # some providers like Dropbox have no scope

    def __str__(self):
        return "{}".format(self.name)

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


class BearerToken(models.Model):
    """
    Token that a bearer (Moogle) can use to get access to OAuth 2.0 protected resources.
    A protected resource belongs to a resource owner (user): it can be a Facebook profile, Google
    Drive documents, tweets on Twitter, ...
    """

    # `user` is the resource owner
    user = models.ForeignKey(User)
    provider = models.ForeignKey(Provider)
    # `_access_token` is json text containing a serialized dictionary like:
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
    _access_token = models.TextField()
    # `updates_cursor` is the cursor used to keep track of the position of the last update.
    # Using a cursor during an update lets us get only the updates happened after the previous
    # update.
    # The cursor is text and it has different forms for different providers
    # E.g. for Dropbox: AAFkqARCY6KnIayYJYqpcIP0-HMWsc4vf21aWJ...RMM1S2V0UoP3Ui_AXIJxtASbBuxveOuKw
    updates_cursor = models.CharField(max_length=200, blank=True)

    objects = BearerTokenManager()

    class Meta:
        unique_together = ("user", "provider")

    def __str__(self):
        return "{}, {}".format(
            self.provider.get_name_display(),
            self.user.get_full_name() or self.user.get_username()
        )

    # Getter and setter properties for _access_token to automatize the conversion from json text
    # to python objects.
    # The getter reads a json string from the db and returns a python dictionary.
    @property
    def access_token(self):
        try:
            return json.loads(self._access_token)
        except ValueError:
            return None

    # The setter receives a python dictionary and stores a json string to the db.
    @access_token.setter
    def access_token(self, value):
        self._access_token = json.dumps(value, indent=4)