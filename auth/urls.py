from django.conf.urls.defaults import patterns, url
from django.contrib.auth import views

from forms import AuthenticationForm

urlpatterns = patterns('',
    url(r'^login/$', views.login, {'authentication_form': AuthenticationForm}),
    url(r'^logout/$', views.logout),
    # TODO: need the oauth urls
)
