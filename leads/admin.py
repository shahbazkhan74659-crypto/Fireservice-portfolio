from django.contrib import admin

from .models import ConsultationRequest, ContactMessage, SurveyRequest


@admin.register(SurveyRequest)
class SurveyRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'resolved')
    list_filter = ('resolved', 'created_at')
    search_fields = ('name', 'email', 'address', 'problem', 'why_survey')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'service', 'created_at', 'resolved')
    list_filter = ('service', 'resolved', 'created_at')
    search_fields = ('name', 'phone', 'email', 'message')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'created_at', 'resolved')
    list_filter = ('resolved', 'created_at')
    search_fields = ('name', 'phone')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
