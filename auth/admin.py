
from gae_django import admin

from models import User

admin.site.register(User, list_display=['username'], 
    list_filter=['is_superuser'], readonly_fields=['password'])
