from django.contrib import admin
from .models import GmailProfile, DriveProfile


class GmailProfileAdmin(admin.ModelAdmin):
    list_display = ['user']


class DriveProfileAdmin(admin.ModelAdmin):
    list_display = ['user']


admin.site.register(GmailProfile, GmailProfileAdmin)
admin.site.register(DriveProfile, DriveProfileAdmin)