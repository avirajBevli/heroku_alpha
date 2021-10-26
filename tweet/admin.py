from django.contrib import admin
from .models import TwitterUser, Tweet

# Register your models here.
admin.site.register(TwitterUser)
admin.site.register(Tweet)

