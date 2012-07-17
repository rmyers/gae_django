
from gettext import gettext as _

from django import forms
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy

class AuthenticationForm(forms.Form):
    """
    Base class for authenticating users. Extend this to get a form that accepts
    username/password logins.
    """
    email = forms.EmailField(label=_("Email"), required=True)
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        """
        If request is passed in, the form will validate that cookies are
        enabled. Note that the request (a HttpRequest object) must have set a
        cookie with the key TEST_COOKIE_NAME and value TEST_COOKIE_VALUE before
        running this validation.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            auth_id = 'email:%s' % email
            self.user_cache = authenticate(auth_id=auth_id, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(_("Please enter a correct username and password. Note that both fields are case-sensitive."))
            elif not self.user_cache.is_active:
                raise forms.ValidationError(_("This account is inactive."))
        self.check_for_test_cookie()
        return self.cleaned_data

    def check_for_test_cookie(self):
        if self.request and not self.request.session.test_cookie_worked():
            raise forms.ValidationError(
                _("Your Web browser doesn't appear to have cookies enabled. "
                  "Cookies are required for logging in."))

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class RegistrationForm(forms.Form):
    
    email = forms.EmailField(
        label=ugettext_lazy("Email Address"))
    username = forms.CharField(
        label=ugettext_lazy("Username"), max_length=16,
        help_text=ugettext_lazy("This will be used as your 'home page' ie /foobar/."))
    password = forms.CharField(
        label=ugettext_lazy('Password'),
        max_length=255, required=True,
        widget=forms.PasswordInput,
    )
    confirm_password = forms.CharField(
        label=ugettext_lazy('Confirm Password'),
        max_length=255, required=True,
        widget=forms.PasswordInput,
    )
    first_name = forms.CharField(
        label=ugettext_lazy('First name'),
        max_length=255, required=True
    )
    last_name = forms.CharField(
        label=ugettext_lazy('Last name'),
        max_length=255, required=False
    )
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        check = self.cleaned_data.get('confirm_password')
        if password != check:
            raise forms.ValidationError(ugettext_lazy("Passwords do not match"))
        
        return check