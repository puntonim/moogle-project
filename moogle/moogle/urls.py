from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'moogle.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Search app
    url(r'^$', 'search.views.home', name='home'),
    url(r'^search/$', 'search.views.search', name='search_search'),

    # Showcase app
    url(r'^tour/$', 'showcase.views.tour', name='showcase_tour'),
    url(r'^about/$', 'showcase.views.about', name='showcase_about'),

    # Accounts app
    url(r'^accounts/', include('accounts.urls')),

    # Tokens app
    url(r'^dashboard/$', 'tokens.views.dashboard', name='tokens_dashboard'),
    url(r'^tokens/', include('tokens.urls')),

    # Profiles app
    url(r'^profile/', include('profiles.urls')),

    # Admin app
    url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
        url(r'^__debug__/', include(debug_toolbar.urls)),
    )