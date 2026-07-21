from django.urls import path

from core.api_views import ContactMessageCreateView, SurveyRequestCreateView
from core.views import ContactPageView, HomeView, SurveyPageView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('survey/', SurveyPageView.as_view(), name='survey'),
    path('api/survey/', SurveyRequestCreateView.as_view(), name='api-survey'),
    path('contact/', ContactPageView.as_view(), name='contact'),
    path('api/contact/', ContactMessageCreateView.as_view(), name='api-contact'),
]
