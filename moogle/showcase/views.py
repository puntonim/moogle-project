from django.shortcuts import render


def tour(request, template='tour.html'):
    args = {}
    return render(request, template, args)

def about(request, template='about.html'):
    args = {}
    return render(request, template, args)