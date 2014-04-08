from django.db import models
from django.contrib.auth.models import User


class AbstractProfile(models.Model):
    """
    Abstract model for profile models.
    It adds the `user` field to all subclasses.
    """
    user = models.ForeignKey(User, unique=True)

    class Meta:
        abstract = True


class GoogleProfile(AbstractProfile):
    """
    Google basic profile info available with scopes:
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    E.g.:
    {
        "locale": "it",
        "family_name": "Coffetti",
        "email": "puntonim@gmail.com",
        "link": "https://profiles.google.com/114986857839554073729",
        "verified_email": true,
        "id": "114986857839554073729",
        "gender": "male",
        "given_name": "Paolo",
        "name": "Paolo Coffetti"
    }
    """
    # `user` is inherited from AbstractProfile.
    family_name = models.CharField(max_length=50, blank=True)  # no idea how long it can be.
    given_name = models.CharField(max_length=50, blank=True)  # no idea how long it can be.
    name = models.CharField(max_length=101, blank=True)  # concat of the previous 2 (w/ a space).
    gender = models.CharField(max_length=10, blank=True)  # the longest should be female (6).
    email = models.EmailField(blank=True)
    # Defaults for a NullBooleanField: blank=True, null=True.
    verified_email = models.NullBooleanField()
    # I guess local can be 2 chars like IT, but also more longer like en_US
    locale = models.CharField(max_length=5, blank=True)
    google_id = models.CharField(max_length=50, blank=True)  # no idea how long it can be.
    link = models.URLField(blank=True)

    def __unicode__(self):
        return self.name or '{} {}'.format(self.given_name, self.family_name)