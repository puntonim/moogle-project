from django.conf.urls import patterns, include, url



urlpatterns = patterns('profiles.views',
    url(r'^$', 'profile', name='profiles_profile'),
)