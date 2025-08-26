from django.contrib import admin
from .models import Profile



class ProfileAdmin(admin.ModelAdmin):
    search_fields = ["user__username"]
    list_display = ["First_name","last_name","Province","date"]

admin.site.register(Profile, ProfileAdmin)
