from webapp2_extras.appengine.auth.models import User as BaseUser
from google.appengine.ext import ndb

from django.template.defaultfilters import slugify

class User(BaseUser):
    """
    Django style user model from the webapp2_extras user model.
    """

    is_superuser = ndb.BooleanProperty(default=False)
    is_staff = ndb.BooleanProperty(default=False)
    is_active = ndb.BooleanProperty(default=True)
    
    # location info
    location = ndb.StringProperty()
    location_slug = ndb.ComputedProperty(lambda self: slugify(self.location))

    def __unicode__(self):
        if self.first_name and self.last_name:
            return self.get_full_name()
        return self.username
    
    @property
    def id(self):
        """Return the id of this user from the key object."""
        return self.key.id()
    
    @property
    def pk(self):
        return self.id

    def is_anonymous(self):
        """
        Always returns False. This is a way of comparing User objects to
        anonymous users.
        """
        return False

    def is_authenticated(self):
        """
        Always return True. This is a way to tell if the user has been
        authenticated in templates.
        """
        return True

    def get_full_name(self):
        "Returns the first_name plus the last_name, with a space in between."
        full_name = u'%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def set_password(self, raw_password):
        from django.contrib.auth.models import get_hexdigest
        if raw_password is None:
            self.set_unusable_password()
        else:
            import random
            algo = 'sha1'
            salt = get_hexdigest(algo, str(random.random()), str(random.random()))[:5]
            hsh = get_hexdigest(algo, salt, raw_password)
            self.password = '%s$%s$%s' % (algo, salt, hsh)

    def check_password(self, raw_password):
        from django.contrib.auth.models import check_password
        if '$' not in self.password:
            return False
        return check_password(raw_password, self.password)

    def set_unusable_password(self):
        from django.contrib.auth.models import UNUSABLE_PASSWORD
        # Sets a value that will never be a valid hash
        self.password = UNUSABLE_PASSWORD

    def has_usable_password(self):
        from django.contrib.auth.models import UNUSABLE_PASSWORD
        if self.password is None \
            or self.password == UNUSABLE_PASSWORD:
            return False
        else:
            return True
    
    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return False
    
    def has_perm(self, perm):
        if self.is_superuser:
            return True
        return False