GAE Django Helper
=================

This project allows you to use the django admin interface on 
google appengine without using django-norel or other wierd
hacks. This is a set of tools such as a custom ModelAdmin
and AdminSite which work with appengine instead of against it.

Who Should Use This?
===================

Since this involves very little hacking it should be suitable
for small projects. But if you need to view > 1000 objects you
should really think twice as the django admin is not designed
for your large dataset. 

Also if you want a quick way to have oauth support for your app
and don't care about the admin stuff the auth app works standalone.
This is based off the work of git://github.com/mikeknapp/AppEngine-OAuth-Library

Current Admin Options Support
=============================

* list_display
* list_filter (BooleanProperty only)
* list_per_page
* form
* exclude
* fields
* fieldsets
* list_display_links
* readonly_fields

In the works:

* inline forms
* search
* actions
* more?

Setup
=====

Install the gae_django app in the root of your Appengine project
or on the sys.path somewhere in it. Use Django like normal except
use google db.Model/properties. 

settings::

    
    DATABASES = {
        'default': {
            'ENGINE': 'gae_django.db.gae', 
            'NAME': '', 
            'USER': '',
            'PASSWORD': '',
            'HOST': '',
            'PORT': '',
        }
    }
    
    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.sites',
        'gae_django.admin',
        'gae_django.auth',
    ]
    
    AUTHENTICATION_BACKENDS = [
        'gae_django.auth.backend.GAEBackend', 
        'gae_django.auth.backend.GAETwitterBackend'
    ]
    
    SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
    MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
    SESSION_SAVE_EVERY_REQUEST = True
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'TIMEOUT': 3600*24*2, # Two Weeks
        }
    }

To use memcache in appengine simply add a module in your root called ``memcache.py`` 
that just imports googles memcache::

    from google.appengine.api.memcache import *

In your urls.py add the following::

    from gae_django import admin
    admin.autodiscover()
    urlpatterns = patterns('',
       url(r'^admin/', include(admin.site.urls)),
       ...
    )

In your apps just add the ``admin.py`` module like this::

    from gae_django import admin

    from models import ModelOne, ModelTwo

    admin.site.register(ModelOne, list_display=['field_one', 'field_two'])
    
    class OtherWay(admin.ModelAdmin):
        list_display = ['field_one', 'field_two']

    admin.site.register(ModelTwo, OtherWay)

Now setup a user for yourself and go to town, this is slightly more tricky
as you'll need to have an User object that is a superuser and all that.
In the future we'll have an easy way to do that as well. For now use
the good ol google admin page located at http://localhost:8080/_ah/admin/ 
