from django.conf import settings
from django import http, forms
from django.shortcuts import redirect, render_to_response
from django.contrib.auth import authenticate, SESSION_KEY,\
    BACKEND_SESSION_KEY

import oauth
from models import User
from forms import RegistrationForm
from django.template.context import RequestContext

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

def register(request, template_name='registration/register.html',
    registration_form=RegistrationForm,
    post_create_callback=None,
    current_app=None, extra_context=None):
    
    if request.method == "POST":
        form = registration_form(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.pop('email')
            username = form.cleaned_data.pop('username')
            password = form.cleaned_data.pop('password')
            del form.cleaned_data['confirm_password']

            auth_id = 'email:%s' % email
            created, user = User.create_user(auth_id, **form.cleaned_data)
            if not created:
                raise forms.ValidationError('Email is not unique %s' % auth_id)
            
            user.set_password(password)
            user.add_username(username)
            user.put()
            
            if post_create_callback:
                post_create_callback(user)
            
            # Authenticate and log them in
            user = authenticate(auth_id=auth_id, password=password)
            login_user(request, user)
            
            return redirect(settings.LOGIN_REDIRECT_URL)
    
    else:
        form = registration_form()
    
    return render_to_response(template_name, {'form': form},
        context_instance=RequestContext(request))         

def twitter_verify(request):

    auth_token = request.REQUEST.get("oauth_token")
    auth_verifier = request.REQUEST.get("oauth_verifier")
    
    if not (auth_token or auth_verifier):
        return redirect('/')
    
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
    
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    client = oauth.TwitterClient(consumer_key, consumer_secret, callback_url)
    return redirect(client.get_authenticate_url())

def github_signin(request):
    """
    Login or signup with github.
    """
    consumer_key = settings.GITHUB_CONSUMER_KEY
    consumer_secret = settings.GITHUB_CONSUMER_SECRET
    callback_url = settings.GITHUB_CALLBACK
    
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    
    client = oauth.GithubClient(consumer_key, consumer_secret, callback_url)
    return redirect(client.get_authorization_url())

def github_link(request):
    """
    Link an existing account to Github
    """

def github_verify(request):
    
    code = request.REQUEST.get("code")
    if not code:
        # user did not authorize?
        return redirect('/')
    
    user = authenticate(github_code=code)
    login_user(request, user)
    
    return redirect(settings.LOGIN_REDIRECT_URL)
    
    