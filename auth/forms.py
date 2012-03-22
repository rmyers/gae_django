
from google.appengine.ext.db import djangoforms
from django import forms

from models import User

class AuthenticationForm(forms.Form):
    """Simple authentication form for email/password."""
    
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, widget=forms.PasswordInput)

    
class SignupForm(djangoforms.ModelForm): 
    class Meta:
        model = User
        exclude = ['picture_url', 'service', 'token', 'is_superuser', 
                   'is_staff', 'is_active', 'date_joined']