from django.conf.urls.defaults import patterns, url

from forms import AuthenticationForm

urlpatterns = patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', 
        {'authentication_form': AuthenticationForm}, name="gae-django-login"),
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    url(r'^register/$', 'gae_django.auth.views.register', name="gae-django-register"),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change'),
    url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done'),
    url(r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
    url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
    url(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm'),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
    
    # SOCIAL AUTH
    url(r'^twitter/$', 'gae_django.auth.views.twitter_request'),
    url(r'^twitter/verify/$', 'gae_django.auth.views.twitter_verify'),
    url(r'^twitter/signin/$', 'gae_django.auth.views.twitter_signin'),
    url(r'^github/verify/$', 'gae_django.auth.views.github_verify'),
    url(r'^github/signin/$', 'gae_django.auth.views.github_signin'),
)
