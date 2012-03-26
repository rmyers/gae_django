from django import template
from ..models import LogEntry

register = template.Library()

@register.inclusion_tag('admin/gae_admin_log.html', takes_context=False)
def gae_admin_log(limit, user_id):
    if not isinstance(user_id, (basestring, int, long)):
        user_id = user_id.id
    limit = int(limit)
    user_id = int(user_id)
    return {
        'user_id': user_id,
        'admin_log': LogEntry.all().filter('user_id', user_id).order('-action_time').fetch(limit)
    }