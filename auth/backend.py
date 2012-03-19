from django.contrib.auth.backends import ModelBackend
from django.conf import settings

class GAEBackend(ModelBackend):
    
    supports_object_permissions = True
    supports_anonymous_user = True
    supports_inactive_user = True
    
    def authenticate(self, email=None, password=None):
        """Support logging in as a normal user"""
        from .models import User
        user = User.all().filter('email', email).get()
        if user is None:
            return None
        
        if user.check_password(password):
            return user

    def get_user(self, user_id):
        """
        Get the user by key, GAE db.get returns None if not found,
        which is exactly what we want here.
        """
        from google.appengine.ext import db
        key = db.Key().from_path('User', int(user_id))
        return db.get(key)
    
    def has_perm(self, user_obj, perm, obj=None):
        if user_obj.is_admin:
            return True
        return False
    
    def get_all_permissions(self, user_obj, obj=None):
        raise NotImplementedError
    
    def get_group_permissions(self, user_obj, obj=None):
        raise NotImplementedError

class GAETwitterBackend(GAEBackend):
    
    def authenticate(self, auth_token=None, auth_verifier=None):
        import oauth
        from .models import User
        consumer_key = settings.TWITTER_CONSUMER_KEY
        consumer_secret = settings.TWITTER_CONSUMER_SECRET
        callback_url = settings.TWITTER_CALLBACK
        
        client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)
        user_info = client.get_user_info(auth_token, auth_verifier=auth_verifier)

        return User.from_twitter_info(user_info)