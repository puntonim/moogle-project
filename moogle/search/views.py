# Stdlib imports
# E.g.: from math import sqrt

# Core Django imports
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

# Third-party app imports
# E.g.: from django_extensions.db.models import TimeStampedModel

# Imports from local apps
from tokens.models import BearerToken, Provider
from utils.solr import Solr, CORE_NAMES


def home(request, template='home.html'):
    if not request.user.is_authenticated():
        return redirect('showcase_tour')

    args = {
    }
    args.update(BearerToken.objects.providers_breakdown_for_user(request.user))
    return render(request, template, args)


@login_required
def search(request, template='search.html'):

    if request.GET.get('twitter', False):
        twitter_results = search_twitter(request.user, request.GET.get('q', ''))

    args = {
        'gets': request.GET,
    }
    return render(request, template, args)


def search_twitter(user, q):
    bearertoken = BearerToken.objects.get(user=user, provider__name=Provider.NAME_TWITTER)\
        .only('id')
    fq = 'bearertoken_id:{}'.format(bearertoken.id)

    solr = Solr(CORE_NAMES[Provider.NAME_TWITTER])
    r = solr.search(q=q, fq=fq)
    print(r.total_results)