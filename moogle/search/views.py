# Stdlib imports
# E.g.: from math import sqrt

# Core Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# Third-party app imports
# E.g.: from django_extensions.db.models import TimeStampedModel

# Imports from local apps
from tokens.models import BearerToken, Provider
from .snooper import Snooper


def home(request, template='home.html'):
    if not request.user.is_authenticated():
        return redirect('showcase_tour')

    args = {
        'name_drive': Provider.NAME_DRIVE,
        'name_gmail': Provider.NAME_GMAIL,
        'name_facebook': Provider.NAME_FACEBOOK,
        'name_twitter': Provider.NAME_TWITTER,
        'name_dropbox': Provider.NAME_DROPBOX,
    }
    args.update(BearerToken.objects.providers_breakdown_for_user(request.user))
    return render(request, template, args)


@login_required
def search(request, template='search.html'):
    q = request.GET.get('q', '')
    args = dict()
    for provider_name, __ in Provider.NAME_CHOICES:
        is_selected = True if request.GET.get(provider_name, '').lower() == 'true' else False
        args['{}_is_selected'.format(provider_name)] = is_selected

        results = Snooper(provider_name, request.user).search(q) if is_selected else []
        args['{}_results'.format(provider_name)] = results

    return render(request, template, args)