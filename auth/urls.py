from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views

from forms import AuthenticationForm

urlpatterns = patterns('gae_django.auth.views',
    url(r'^login/$', views.login, {'authentication_form': AuthenticationForm}),
    url(r'^logout/$', views.logout),
    url(r'^twitter/$', 'twitter_request'),
    url(r'^twitter/verify/$', 'twitter_verify'),
    url(r'^twitter/signin/$', 'twitter_signin'),
)
