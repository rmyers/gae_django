
from gettext import gettext as _

from google.appengine.ext import db
from django.utils.safestring import mark_safe
from django.contrib.admin.models import DELETION, CHANGE, ADDITION
from django.contrib.admin.util import quote

class User(object):
    """Make a fake user object as the original has a foriegn key."""
    
    def __init__(self, log):
        self.id = log.user_id
        self.name = log.user_name
    
    def get_full_name(self):
        return self.name

class LogEntry(db.Model):
    action_time = db.DateTimeProperty(auto_now=True)
    user_id = db.IntegerProperty()
    user_name = db.StringProperty(indexed=False)
    content_type = db.StringProperty(indexed=False)
    app_label = db.StringProperty(indexed=False)
    object_id = db.StringProperty(indexed=False)
    object_repr = db.StringProperty(indexed=False)
    action_flag = db.IntegerProperty(indexed=False)
    change_message = db.StringProperty(indexed=False)

    class Meta:
        verbose_name = _('log entry')
        verbose_name_plural = _('log entries')
        db_table = 'django_admin_log'
        ordering = ('-action_time',)

    def __repr__(self):
        return str(self.action_time)
    
    _user = None

    @property
    def user(self):
        if not self._user:
            self._user = User(self)
        return self._user
    
    def is_addition(self):
        return self.action_flag == ADDITION

    def is_change(self):
        return self.action_flag == CHANGE

    def is_deletion(self):
        return self.action_flag == DELETION

    def get_edited_object(self):
        "Returns the edited object represented by this log entry"
        return self.parent()

    def get_admin_url(self):
        """
        Returns the admin URL to edit the object represented by this log entry.
        This is relative to the Django admin index page.
        """
        if self.content_type and self.object_id:
            return mark_safe(u"%s/%s/%s/" % (self.app_label, self.content_type, quote(self.object_id)))
        return None