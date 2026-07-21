from django.urls import path

from core.api_views import ContactMessageCreateView, SurveyRequestCreateView
from core.views import (
    AboutView,
    BrochureView,
    CertificationsView,
    ClienteleView,
    ContactPageView,
    HomeView,
    ProcessView,
    ServicesView,
    SurveyPageView,
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('clientele/', ClienteleView.as_view(), name='clientele'),
    path('services/', ServicesView.as_view(), name='services'),
    path('process/', ProcessView.as_view(), name='process'),
    path('brochure/', BrochureView.as_view(), name='brochure'),
    path('certifications/', CertificationsView.as_view(), name='certifications'),
    path('survey/', SurveyPageView.as_view(), name='survey'),
    path('api/survey/', SurveyRequestCreateView.as_view(), name='api-survey'),
    path('contact/', ContactPageView.as_view(), name='contact'),
    path('api/contact/', ContactMessageCreateView.as_view(), name='api-contact'),
]
