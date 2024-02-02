from django.contrib import admin

from ..user.models import User, Temp

admin.site.register(User)
admin.site.register(Temp)