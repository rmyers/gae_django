
from gae_django import admin

from models import User

admin.site.register(User, list_display=['first_name', 'last_name'], 
    list_filter=['is_superuser'], readonly_fields=['password'])
