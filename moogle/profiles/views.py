from django.contrib.auth.decorators import login_required
from django.shortcuts import render



@login_required
def profile(request, template='profile.html'):
    args = {}
    return render(request, template, args)
