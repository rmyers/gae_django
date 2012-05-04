from django.conf import settings
from django.shortcuts import redirect
from django.contrib.auth import authenticate, SESSION_KEY,\
    BACKEND_SESSION_KEY, logout

import oauth

def login_user(request, user):
    """
    Persist a user id and a backend in the request. This way a user doesn't
    have to reauthenticate on every request.
    """
    if user is None:
        user = request.user
    # TODO: It would be nice to support different login methods, like signed cookies.
    if SESSION_KEY in request.session:
        if request.session[SESSION_KEY] != user.id:
            # To avoid reusing another user's session, create a new, empty
            # session if the existing session corresponds to a different
            # authenticated user.
            request.session.flush()
    else:
        request.session.cycle_key()
    request.session[SESSION_KEY] = user.id
    request.session[BACKEND_SESSION_KEY] = user.backend
    if hasattr(request, 'user'):
        request.user = user

def twitter_verify(request):

    auth_token = request.REQUEST.get("oauth_token")
    auth_verifier = request.REQUEST.get("oauth_verifier")

    user = authenticate(auth_token=auth_token, auth_verifier=auth_verifier)
    login_user(request, user)
    
    return redirect(settings.LOGIN_REDIRECT_URL)

def twitter_request(request):
    """
    Login or signup a user with twitter.
    """
    consumer_key = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET
    callback_url = settings.TWITTER_CALLBACK
        
    client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)
    return redirect(client.get_authorization_url())

def twitter_signin(request):
    """Signin a user through twitter."""
    consumer_key = settings.TWITTER_CONSUMER_KEY
    consumer_secret = settings.TWITTER_CONSUMER_SECRET
    callback_url = settings.TWITTER_CALLBACK
        
    client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)
    return redirect(client.get_authenticate_url())
