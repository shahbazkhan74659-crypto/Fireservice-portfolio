from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from leads.serializers import (
    ConsultationRequestSerializer,
    ContactMessageSerializer,
    SurveyRequestSerializer,
)


class SurveyRequestCreateView(CreateAPIView):
    queryset = SurveyRequest.objects.all()
    serializer_class = SurveyRequestSerializer
    permission_classes = [AllowAny]  # overrides the global IsAuthenticated default
    # No explicit throttle_classes needed — AnonRateThrottle ('10/min') already
    # applies via REST_FRAMEWORK.DEFAULT_THROTTLE_CLASSES.


class ContactMessageCreateView(CreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]  # overrides the global IsAuthenticated default


class ConsultationRequestCreateView(CreateAPIView):
    queryset = ConsultationRequest.objects.all()
    serializer_class = ConsultationRequestSerializer
    permission_classes = [AllowAny]  # overrides the global IsAuthenticated default
