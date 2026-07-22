import json

from django.contrib.auth import authenticate, login
from django.db.models import Max
from django.http import JsonResponse
from django.views import View
from rest_framework.generics import CreateAPIView, ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from leads.serializers import (
    ConsultationRequestSerializer,
    ContactMessageSerializer,
    SurveyRequestSerializer,
)
from website.models import ClientLogo, MissionVisionItem
from website.serializers import ClientLogoSerializer, MissionVisionItemSerializer


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


class AdminHubLoginAPIView(View):
    """Plain Django view, not DRF, on purpose: DRF's APIView marks itself
    csrf_exempt and SessionAuthentication.enforce_csrf() only runs once a
    user is already attached to the request, so a DRF view here would
    silently skip CSRF checking on the one request (an anonymous login POST)
    where that check actually matters. A plain View still goes through
    CsrfViewMiddleware normally."""

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'detail': ['Invalid request.']}, status=400)

        username = (data.get('username') or '').strip()
        password = data.get('password') or ''
        if not username or not password:
            return JsonResponse({'detail': ['Username and password are required.']}, status=400)

        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({'detail': ['Invalid username or password.']}, status=401)

        login(request, user)
        return JsonResponse({'detail': ['Logged in.']})


class MissionVisionItemListView(ListAPIView):
    # No permission_classes override — the project-wide IsAuthenticated +
    # SessionAuthentication default is exactly what's wanted here (admin-hub
    # only), unlike the public lead-capture endpoints above which opt out of it.
    queryset = MissionVisionItem.objects.all()
    serializer_class = MissionVisionItemSerializer


class MissionVisionItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MissionVisionItem.objects.all()
    serializer_class = MissionVisionItemSerializer


class ClientLogoListCreateView(ListCreateAPIView):
    queryset = ClientLogo.objects.all()
    serializer_class = ClientLogoSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON

    def perform_create(self, serializer):
        next_order = (ClientLogo.objects.aggregate(Max('order'))['order__max'] or 0) + 1
        serializer.save(order=next_order)


class ClientLogoDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ClientLogo.objects.all()
    serializer_class = ClientLogoSerializer
    parser_classes = [MultiPartParser, FormParser]
