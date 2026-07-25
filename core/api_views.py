import json

from django.contrib.auth import authenticate, login
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.views import View
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAdminUser

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from leads.serializers import (
    ConsultationRequestSerializer,
    ContactMessageSerializer,
    SurveyRequestSerializer,
)
from website.models import Brand, Certification, ClientLogo, FireRiskAssessmentItem, MissionVisionItem, Product, Service, SiteSetting
from website.serializers import (
    BrandSerializer,
    CertificationSerializer,
    ClientLogoSerializer,
    FireRiskAssessmentItemSerializer,
    MissionVisionItemSerializer,
    ProductSerializer,
    ServiceSerializer,
    SiteSettingSerializer,
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
        # Reject non-staff accounts the same way as a wrong password: same
        # status code, same message, no login() call. This is deliberately
        # indistinguishable from bad credentials so a login attempt can't be
        # used to enumerate which usernames exist but merely lack Admin Hub
        # access.
        if user is None or not user.is_staff:
            return JsonResponse({'detail': ['Invalid username or password.']}, status=401)

        login(request, user)
        return JsonResponse({'detail': ['Logged in.']})


class MissionVisionItemListView(ListAPIView):
    # Explicit IsAdminUser (checks request.user.is_staff) rather than relying
    # on the project-wide IsAuthenticated default — any authenticated but
    # non-staff account must not reach Admin Hub content management.
    queryset = MissionVisionItem.objects.all()
    serializer_class = MissionVisionItemSerializer
    permission_classes = [IsAdminUser]


class MissionVisionItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = MissionVisionItem.objects.all()
    serializer_class = MissionVisionItemSerializer
    permission_classes = [IsAdminUser]


class ClientLogoListCreateView(ListCreateAPIView):
    queryset = ClientLogo.objects.all()
    serializer_class = ClientLogoSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        # transaction.atomic() + select_for_update() closes the read-then-write
        # TOCTOU race between concurrent creates computing the same next_order —
        # works on both SQLite (no-op lock, but the file-level write lock
        # serializes writers anyway) and MySQL (a real row lock).
        with transaction.atomic():
            next_order = (ClientLogo.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class ClientLogoDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ClientLogo.objects.all()
    serializer_class = ClientLogoSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]


class BrandListCreateView(ListCreateAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (Brand.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class BrandDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]


class ServiceListCreateView(ListCreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (Service.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class ServiceDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]


class ProductListCreateView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (Product.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]


class CertificationListCreateView(ListCreateAPIView):
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (Certification.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class CertificationDeleteView(DestroyAPIView):
    # DestroyAPIView only, not RetrieveUpdateDestroyAPIView — Certifications
    # deliberately have no Edit (per explicit product decision), so PATCH/PUT
    # aren't exposed at all rather than being wired up and unused.
    queryset = Certification.objects.all()
    serializer_class = CertificationSerializer
    permission_classes = [IsAdminUser]


class FireRiskAssessmentItemListCreateView(ListCreateAPIView):
    # Plain text, no file upload — default JSON parser is fine here, unlike
    # the image-backed models above.
    queryset = FireRiskAssessmentItem.objects.all()
    serializer_class = FireRiskAssessmentItemSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (FireRiskAssessmentItem.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class FireRiskAssessmentItemDetailView(RetrieveUpdateDestroyAPIView):
    queryset = FireRiskAssessmentItem.objects.all()
    serializer_class = FireRiskAssessmentItemSerializer
    permission_classes = [IsAdminUser]


class SiteSettingDetailView(RetrieveUpdateAPIView):
    # Singleton, not list/create — get_object always resolves to the one
    # pk=1 row (creating it on first access) rather than looking up a pk
    # from the URL, so there's nothing to list or create.
    serializer_class = SiteSettingSerializer
    permission_classes = [IsAdminUser]

    def get_object(self):
        return SiteSetting.load()
