import logging

from django.contrib.auth.backends import ModelBackend
from django.conf import settings

from models import User

class GAEBackend(ModelBackend):
    
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True
    
    def authenticate(self, auth_id=None, password=None):
        """Support logging in as a normal user"""
        user = User.get_by_auth_password(auth_id, password)
        if user is None:
            return None

    def get_user(self, user_id):
        """
        Get the user by key, GAE db.get returns None if not found,
        which is exactly what we want here.
        """
        from google.appengine.ext import ndb
        user_key = ndb.Key('User', int(user_id))
        future = user_key.get_async()
        return future.get_result()
    
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_admin:
            return True
        return False
    
    def get_all_permissions(self, user_obj, obj=None):
        raise NotImplementedError
    
    def get_group_permissions(self, user_obj, obj=None):
        raise NotImplementedError
    
    def user_from_info(self, info):
        """Get or create a user from the oauth providers info.
        
        * info: dict in the form::
        
            {
                'first_name': fname,
                'last_name': lname,
                'location': info.get('location', "Pythonville, USA"),
                'description': info.get('description', ''),
                'url': info.get('url'),
                'picture_url': info.get('picture', ''),
                # Default username
                'username': info['username'],
                'auth_id': 'twitter:username'
            }
        """
        from random import randint
        
        auth_id = info.pop('auth_id')
        username = info.pop('username')
        user = User.get_by_auth_id(auth_id)

        if user is None:
            created, user = User.create_user(auth_id, **info)
            if not created:
                raise Exception('Auth ID is not unique %s' % auth_id)
            
            # Add the username as an auth_id, Add _# on the end until successful
            # don't loop forever tho, try a few times then give up.
            added = False
            for attempt in xrange(10):
                _username = username
                if attempt:
                    logging.error("Unable to add username: %s", _username)
                    # try to make the name unique
                    _username = '%s%s' % (username, randint(1,100))
                added, _ = user.add_auth_id('own:%s' % _username)
                if added:
                    break
            
            if not added:
                raise Exception('Unable to add username: %s' % username)

        return user

class GAETwitterBackend(GAEBackend):
    
    def authenticate(self, auth_token=None, auth_verifier=None):
        import oauth
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET
        callback_url = settings.TWITTER_CALLBACK
        
        client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)
        user_info = client.get_user_info(auth_token, auth_verifier=auth_verifier)
  
        return self.user_from_info(self._parse_info(user_info))
    
    def _parse_info(self, info):
        """Parse the raw info from twitter for creating a new user."""
        name = info.get('name', 'Joe Doe').split()
        if len(name) < 2:
            fname = name[0]
            lname = ''
        else:
            fname = name[0]
            lname = name[1]
        data = {
            'first_name': fname,
            'last_name': lname,
            'location': info.get('location', ""),
            'description': info.get('description', ''),
            'url': info.get('url'),
            'picture_url': info.get('picture', ''),
            # Default username
            'username': info['username'],
            'auth_id': 'twitter:%s' % info['username']
        }
        return data

class GAEGithubBackend(GAEBackend):
    
    def authenticate(self, github_code=None):
        import oauth
        consumer_key = settings.GITHUB_CONSUMER_KEY
        consumer_secret = settings.GITHUB_CONSUMER_SECRET
        callback_url = settings.GITHUB_CALLBACK
        
        client = oauth.GithubClient(consumer_key, consumer_secret, callback_url)
        user_info = client.get_user_info(code=github_code)
        
        return self.user_from_info(self._parse_info(user_info))
    
    def _parse_info(self, info):
        
        name = info.get('name', 'Joe Doe').split()
        if len(name) < 2:
            fname = name[0]
            lname = ''
        else:
            fname = name[0]
            lname = name[1]
        data = {
            'first_name': fname,
            'last_name': lname,
            'location': info.get('location', ""),
            'description': info.get('bio', ''),
            'url': info.get('blog_url'),
            'picture_url': info.get('avatar_url', ''),
            # Default username
            'username': info['login'],
            'auth_id': 'github:%s' % info['login'],
            'github_access_token': info['access_token']
        }
        return data
        