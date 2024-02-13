from django.contrib import admin

from ..user.models import User, Temp,Profile

admin.site.register(User)
admin.site.register(Temp)
admin.site.register(Profile)