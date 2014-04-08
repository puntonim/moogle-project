from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse


def signup(request):
    if request.user.is_authenticated():
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Create the new user
            form.save()
            # Login the new user
            new_user = authenticate(username=form.cleaned_data["username"],
                                    password=form.cleaned_data["password2"])
            login(request, new_user)
            return redirect(reverse('home'))
    else:
        form = UserCreationForm()

    return render(request, "signup.html", {'form': form})