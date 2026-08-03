from django.contrib import admin

from .models import Brand, Brochure, Certification, ClientLogo, FireRiskAssessmentItem, HeroSlide, MissionVisionItem, Product, ProcessPhase, Service, SiteSetting


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


@admin.register(ProcessPhase)
class ProcessPhaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order', 'id')


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'order')
    ordering = ('order', 'id')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'meta', 'order')
    ordering = ('order', 'id')


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    # '__str__' rather than a raw field name — the changelist's one row is a
    # singleton, so its link should read "Site Settings", not just "10"
    # (whatever years_experience happens to be).
    list_display = ('__str__',)

    def has_add_permission(self, request):
        # Singleton — the seed migration already created pk=1, adding
        # another row would just be an orphaned, never-read duplicate.
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Brochure)
class BrochureAdmin(admin.ModelAdmin):
    # Singleton, same pattern as SiteSettingAdmin above.
    list_display = ('__str__',)

    def has_add_permission(self, request):
        return not Brochure.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
