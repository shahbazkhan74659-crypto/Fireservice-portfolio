from django.contrib import admin

from .models import ClientLogo, MissionVisionItem


@admin.register(MissionVisionItem)
class MissionVisionItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order', 'id')


@admin.register(ClientLogo)
class ClientLogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'id')
