from django.db import models


class BearerTokenManager(models.Manager):
    def providers_breakdown_for_user(self, user):
        """
        Generate a breakdown which shows if a given `User` has the specific `BearerToken` for
        each `Provider` in the system.
        Return a dict.
        Example:
        >>> u = User.objects.get(id=1)
        >>> BearerToken.objects.providers_breakdown_for_user(user)
        {
            'gmail': False,
            'drive': True,
            'facebook': True,
            'twitter': False,
            'dropbox': False,
            'is_any_provider': True,
            'is_all_providers': False,
        }
        Where:
            - The key (like 'gmail') is a `Provider.name`.
            - The value (like False) shows if that provider was added by the user (so if
              there is a BearerToken for that `User` and that `Provider`).
            - `is_any_provider` is True if ANY of `is_added` is True
            - `is_all_providers` is True if ALL of `is_added` are True
        """

        # Note that there can easily be some import issues w/ managers.
        # If we import from a global scope (like at the top of this file):
        #   from .models import Provider
        # this will generate a circular import problem because in models we import this manager.
        # This is the reason why we import here.
        from .models import Provider

        tokens = self.model.objects.filter(user=user)
        added_providers = [x.provider for x in tokens]
        breakdown = {}
        for p in Provider.objects.all():
            breakdown[p.name] = p in added_providers
        breakdown['is_any_provider'] = len(added_providers) > 0
        breakdown['is_all_providers'] = len(added_providers) == Provider.objects.count()
        return breakdown