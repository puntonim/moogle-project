from django.contrib import admin
from .models import Provider, BearerToken


class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name']

admin.site.register(Provider, ProviderAdmin)
admin.site.register(BearerToken)