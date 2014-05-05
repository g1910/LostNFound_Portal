from django.contrib import admin
from LostNFound.models import Tags, Categories, UserDetails, User, Lost, Found

admin.site.register(Tags)
admin.site.register(Categories)
admin.site.register(UserDetails)
admin.site.register(User)
admin.site.register(Lost)
admin.site.register(Found)
