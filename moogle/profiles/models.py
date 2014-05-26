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
    Abstract Google basic profile info available with scopes:
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    E.g.:
    {
        "locale": "en",
        "family_name": "Doe",
        "email": "johndoe@gmail.com",
        "link": "https://profiles.google.com/353452857839983457489",
        "verified_email": true,
        "id": "353452857839983457489",
        "gender": "male",
        "given_name": "John",
        "name": "John Doe"
    }
    """
    # `user` is inherited from AbstractProfile.
    family_name = models.CharField(max_length=50, blank=True)  # No idea how long it can be.
    given_name = models.CharField(max_length=50, blank=True)  # No idea how long it can be.
    name = models.CharField(max_length=101, blank=True)  # Concat of the previous 2 (w/ a space).
    gender = models.CharField(max_length=10, blank=True)  # The longest should be female (6).
    email = models.EmailField(blank=True)
    # Defaults for a NullBooleanField: blank=True, null=True.
    verified_email = models.NullBooleanField()
    # I guess locale can be 2 chars like IT, but also more longer like en_US.
    locale = models.CharField(max_length=5, blank=True)
    google_id = models.CharField(max_length=50, blank=True)  # No idea how long it can be.
    link = models.URLField(blank=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name or '{} {}'.format(self.given_name, self.family_name)


class GmailProfile(GoogleProfile):
    """
    Concrete Google Gmail basic profile model.
    """
    pass


class DriveProfile(GoogleProfile):
    """
    Concrete Google Drive basic profile model.
    """
    pass