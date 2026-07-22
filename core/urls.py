from django.contrib.auth.views import LogoutView
from django.urls import path

from core.api_views import (
    AdminHubLoginAPIView,
    ClientLogoDetailView,
    ClientLogoListCreateView,
    ConsultationRequestCreateView,
    ContactMessageCreateView,
    MissionVisionItemDetailView,
    MissionVisionItemListView,
    SurveyRequestCreateView,
)
from core.views import (
    AboutView,
    AdminHubClienteleView,
    AdminHubHomeView,
    AdminHubLoginView,
    BrochureView,
    CertificationsView,
    ClienteleView,
    ConsultationView,
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
    path('consultation/', ConsultationView.as_view(), name='consultation'),
    path('api/consultation/', ConsultationRequestCreateView.as_view(), name='api-consultation'),
    path('admin-hub/', AdminHubLoginView.as_view(), name='adminhub-login'),
    path('api/admin-hub/login/', AdminHubLoginAPIView.as_view(), name='api-adminhub-login'),
    path('admin-hub/home/', AdminHubHomeView.as_view(), name='adminhub-home'),
    path('admin-hub/clientele/', AdminHubClienteleView.as_view(), name='adminhub-clientele'),
    path('admin-hub/logout/', LogoutView.as_view(next_page='adminhub-login'), name='adminhub-logout'),
    path('api/admin-hub/mission-vision/', MissionVisionItemListView.as_view(), name='api-adminhub-mission-vision-list'),
    path('api/admin-hub/mission-vision/<int:pk>/', MissionVisionItemDetailView.as_view(), name='api-adminhub-mission-vision-detail'),
    path('api/admin-hub/client-logos/', ClientLogoListCreateView.as_view(), name='api-adminhub-client-logos-list'),
    path('api/admin-hub/client-logos/<int:pk>/', ClientLogoDetailView.as_view(), name='api-adminhub-client-logos-detail'),
]
