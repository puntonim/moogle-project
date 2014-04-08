from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'},
        name='accounts_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'},
        name='accounts_logout'),
    url(r'^signup/$', 'accounts.views.signup', name='accounts_signup'),
)