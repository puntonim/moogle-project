from django.conf.urls import patterns, url


urlpatterns = patterns('tokens.views',
    url(r'^add/(?P<provider_name>[A-Za-z-]*)/$', 'add', name='tokens_add'),
    url(r'^add/(?P<provider_name>[A-Za-z-]*)/callback/$', 'callback', name='tokens_callback'),
)