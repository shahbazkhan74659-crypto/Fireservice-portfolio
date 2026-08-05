from django.contrib import admin

from .models import BlogPost, Brand, Brochure, Certification, ClientLogo, FireRiskAssessmentItem, HeroSlide, MissionVisionItem, Product, ProcessPhase, Service, SiteSetting
from .pdf_utils import render_pdf_first_page_to_png


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'published_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}
    ordering = ('-published_at',)


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
    # `image` is server-computed from `pdf` (see save_model below), same
    # contract as BrochureSerializer where it's declared read_only — editing
    # it directly here would let it drift out of sync with the PDF.
    readonly_fields = ('image',)

    def has_add_permission(self, request):
        return not Brochure.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        # This admin bypasses BrochureSerializer.update(), which is the only
        # other place the PDF-first-page render normally happens — without
        # this, replacing the PDF here leaves the preview image stale.
        if 'pdf' in form.changed_data:
            obj.image = render_pdf_first_page_to_png(obj.pdf, 'its-brochure')
        super().save_model(request, obj, form, change)
