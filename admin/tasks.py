"""
Deferred tasks for admin. 
"""

from google.appengine.ext import db

from django.contrib.admin.models import DELETION

from .models import LogEntry

def create_log(user_id, user_name, content_type, app_label, object_id, object_repr, 
               action_flag, change_message=''):
    """Create a addition or change log with the object as the parent."""
    parent = db.Key(object_id)
    log = LogEntry(
        parent = parent,
        user_id = user_id,
        user_name = user_name,
        content_type = content_type,
        app_label = app_label,
        object_id = object_id,
        object_repr = object_repr,
        action_flag = action_flag,
        change_message = change_message
    )
    db.put(log)
    return True
    
def create_deletion_log(user_id, user_name, content_type, app_label, object_id, object_repr):
    """Create a deletion log with no parent."""
    log = LogEntry(
        user_id = user_id,
        user_name = user_name,
        content_type = content_type,
        app_label = app_label,
        object_id = object_id,
        object_repr = object_repr,
        action_flag = DELETION
    )
    db.put(log)
    return True