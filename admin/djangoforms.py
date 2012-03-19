"""
Monkey patch more fields than googles djangoforms
"""

from google.appengine.ext.db.djangoforms import *


class EmailProperty(db.EmailProperty):
    __metaclass__ = monkey_patch
    
    def get_form_field(self, **kwargs):
        """Return a Django form field appropriate for a URL property.
        
        This defaults to a URLField instance.
        """
        defaults = {'form_class': forms.EmailField}
        defaults.update(kwargs)
        return super(EmailProperty, self).get_form_field(**defaults)