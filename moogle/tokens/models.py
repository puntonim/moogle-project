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
    redirect_url = models.CharField(max_length=200)  # Relative url like /tokens/add/drive/callback
    authorization_base_url = models.URLField()
    token_url = models.URLField()
    request_token_url = models.URLField(blank=True)  # Used only in Oauth1
    oauth_version = models.CharField(max_length=5, blank=True)  # e.g. 2 or 1.0a
    _scope = models.TextField(blank=True)  # some providers like Dropbox have no scope

    # `_scope` is json text containing a serialized list like:
    # ["https://www.googleapis.com/auth/userinfo.email", "https://mail.google.com"]
    # A getter and a setter property are defined on this field to automatize the conversion
    # from json text to python  objects.
    #
    # `_scope` has a getter and a setter property to automatize the conversion from json text
    # to python list.
    @property
    def scope(self):
        """
        Getter property for _scope to automatize the conversion from json text to python objects.
        Read a json string from the db and return a python list.
        """
        try:
            return json.loads(self._scope)
        except ValueError:
            return None

    @scope.setter
    def scope(self, value):
        """
        Setter property for _scope to automatize the conversion from json text to python objects.
        Receive a python list and store a json string to the db.
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

    def __str__(self):
        return "{}".format(self.name)


class BearerToken(models.Model):
    """
    Token that a bearer like Moogle and Magpie can use to get access to OAuth 2.0 protected
    resources. A protected resource belongs to a resource owner (user): it can be a Facebook
    profile, Google Drive documents, tweets on Twitter, ...
    """
    # `user` is the resource owner
    user = models.ForeignKey(User)
    provider = models.ForeignKey(Provider)
    _token_set = models.TextField()

    objects = BearerTokenManager()

    # `_token_set` is json text containing a serialized dictionary like:
    #{
    #    "refresh_token": "1/UTY6FA......XHCSIvhm1dghJHHG678",
    #    "expires_in": 3600,
    #    "token_type": "Bearer",
    #    "access_token": "ya29.1.AADtN_VwezbeOQGkJE4_3ZDNZimrRf86Dn...pL8YB1rpVRhav0-mIiHEmV8",
    #    "id_token": "eyJhbGciOiJSUzI1NiIsI...U3MWJlNZoempIreV572mbxH7Rm90eNQwfShPQnI49u8bZgc"
    #}
    # This example is a OAuth2 token (from Google) but it can be also OAuth1 token (like Twitter).
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

    class Meta:
        unique_together = ("user", "provider")

    def __str__(self):
        return "{}, {}".format(
            self.provider.get_name_display(),
            self.user.get_full_name() or self.user.get_username()
        )