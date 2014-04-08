# Stdlib imports
# E.g.: from math import sqrt

# Core Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# Third-party app imports
# E.g.: from django_extensions.db.models import TimeStampedModel

# Imports from local apps
from tokens.models import BearerToken


def home(request, template='home.html'):
    if not request.user.is_authenticated():
        return redirect('showcase_tour')

    args = {
    }
    args.update(BearerToken.objects.providers_breakdown_for_user(request.user))
    return render(request, template, args)

@login_required
def search(request, template='search.html'):
    args = {
        'gets': request.GET,
    }
    return render(request, template, args)


