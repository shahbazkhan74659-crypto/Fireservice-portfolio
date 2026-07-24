from django.contrib import admin

from .models import Brand, ClientLogo, MissionVisionItem


@admin.register(MissionVisionItem)
class MissionVisionItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order')
    ordering = ('order', 'id')


@admin.register(ClientLogo)
class ClientLogoAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'id')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'id')
