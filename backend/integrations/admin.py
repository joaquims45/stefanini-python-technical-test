from django.contrib import admin

from .models import Item, SyncRun

admin.site.register(Item)
admin.site.register(SyncRun)
