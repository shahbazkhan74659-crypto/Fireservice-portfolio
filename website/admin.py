from django.contrib import admin

from .models import Brand, ClientLogo, FireRiskAssessmentItem, MissionVisionItem, Service


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


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'id')


@admin.register(FireRiskAssessmentItem)
class FireRiskAssessmentItemAdmin(admin.ModelAdmin):
    list_display = ('text', 'order')
    ordering = ('order', 'id')
