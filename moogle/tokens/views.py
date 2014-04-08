# Stdlib imports
# E.g.: from math import sqrt

# Core Django imports
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib import messages

# Third-party app imports
# E.g.: from django_extensions.db.models import TimeStampedModel

# Imports from local apps
from .models import Provider, BearerToken
from .oauthlib import OAuthFlowMangerFactory


@login_required
def dashboard(request, template='dashboard.html'):
    args = {
    }
    args.update(BearerToken.objects.providers_breakdown_for_user(request.user))
    return render(request, template, args)


@login_required
def add(request, provider_name):
    """
    Add a new BearerToken for `request.user`. Launch the OAuth protocol.

    Parameters:
    provider_name -- a `Provider.name`
    """
    try:
        provider = Provider.objects.get(name__iexact=provider_name)
    except Provider.DoesNotExist:
        # Such a provider name does not exist
        msg = "Provider {} does not exist.".format(provider_name)
        raise Http404(msg)

    mgr = OAuthFlowMangerFactory.create_oauth_flow_manger(provider)
    authorization_url = mgr.step1(request)
    return redirect(authorization_url)


@login_required
def callback(request, provider_name):
    """
    The call back of the OAuth protocol. Receive the BearerToken.
    """

    # TODO: too similar to add(), refactor it

    try:
        provider = Provider.objects.get(name__iexact=provider_name)
    except Provider.DoesNotExist:
        # Such a provider name does not exist
        msg = "Provider {} does not exist.".format(provider_name)
        raise Http404(msg)

    mgr = OAuthFlowMangerFactory.create_oauth_flow_manger(provider)
    mgr.step2(request)

    messages.success(request, '<strong>Well done!</strong> You can now use <em>{}</em>.'.format(
        provider.get_name_display())
    )

    return redirect(reverse('tokens_dashboard'))






