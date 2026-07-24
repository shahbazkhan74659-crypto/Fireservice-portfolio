from django.contrib import admin

from .models import Brand, Certification, ClientLogo, FireRiskAssessmentItem, MissionVisionItem, Product, Service


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'id')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'meta', 'order')
    ordering = ('order', 'id')
