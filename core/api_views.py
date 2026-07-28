import json

from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.core.cache import cache
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
from rest_framework.response import Response
from rest_framework.views import APIView

from core.serializers import ChangePasswordSerializer, ChangeUsernameSerializer
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
    CsrfViewMiddleware normally.

    Brute-force protection: failed attempts are counted per client IP and
    per attempted username in django.core.cache (no new dependency/model —
    this project has no other rate-limit infrastructure to extend). Either
    counter hitting LOCKOUT_THRESHOLD within LOCKOUT_WINDOW_SECONDS blocks
    further attempts against that IP/username with a 429 until the window
    expires. Uses whatever CACHES backend is configured (the project has none
    explicitly set, so this runs on Django's default local-memory cache) —
    fine for this single-process dev/staging setup, but that cache is
    per-process, so it would NOT enforce a shared lockout across multiple
    worker processes/machines in a real multi-process production deployment;
    a shared backend (e.g. Redis/memcached) would be needed for that.
    """

    LOCKOUT_THRESHOLD = 5
    LOCKOUT_WINDOW_SECONDS = 5 * 60  # 5 minutes

    @staticmethod
    def _client_ip(request):
        # No reverse-proxy trust is configured anywhere in this project for
        # client-IP purposes (SECURE_PROXY_SSL_HEADER in prod.py only trusts
        # X-Forwarded-Proto for SSL detection, not X-Forwarded-For for the
        # client address) — trusting X-Forwarded-For here would let an
        # attacker spoof a fresh IP on every request and bypass the lockout
        # entirely, so REMOTE_ADDR is used unconditionally.
        return request.META.get('REMOTE_ADDR', '')

    def _locked_out(self, ip_key, user_key):
        if ip_key and cache.get(ip_key, 0) >= self.LOCKOUT_THRESHOLD:
            return True
        if user_key and cache.get(user_key, 0) >= self.LOCKOUT_THRESHOLD:
            return True
        return False

    def _record_failure(self, key):
        if not key:
            return
        # add()/incr() rather than get()-then-set() to avoid losing counts to
        # a read-then-write race between concurrent requests; add() seeds the
        # key only if it doesn't already exist (first failure in the window).
        if not cache.add(key, 1, self.LOCKOUT_WINDOW_SECONDS):
            try:
                cache.incr(key)
            except ValueError:
                # Key expired between the add() and incr() calls — reseed it.
                cache.set(key, 1, self.LOCKOUT_WINDOW_SECONDS)

    def post(self, request):
        ip = self._client_ip(request)
        ip_key = f'adminhub_login_fail:ip:{ip}' if ip else None

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'detail': ['Invalid request.']}, status=400)

        username = (data.get('username') or '').strip()
        password = data.get('password') or ''

        user_key = f'adminhub_login_fail:user:{username.lower()}' if username else None

        if self._locked_out(ip_key, user_key):
            return JsonResponse(
                {'detail': ['Too many failed login attempts. Please try again in a few minutes.']},
                status=429,
            )

        if not username or not password:
            return JsonResponse({'detail': ['Username and password are required.']}, status=400)

        user = authenticate(request, username=username, password=password)
        # Reject non-staff accounts the same way as a wrong password: same
        # status code, same message, no login() call. This is deliberately
        # indistinguishable from bad credentials so a login attempt can't be
        # used to enumerate which usernames exist but merely lack Admin Hub
        # access.
        if user is None or not user.is_staff:
            self._record_failure(ip_key)
            self._record_failure(user_key)
            return JsonResponse({'detail': ['Invalid username or password.']}, status=401)

        # Successful login clears both counters so a legitimate user who
        # mistyped their password a few times isn't left partway toward a
        # lockout from stale failures.
        if ip_key:
            cache.delete(ip_key)
        if user_key:
            cache.delete(user_key)

        login(request, user)
        return JsonResponse({'detail': ['Logged in.']})


class AdminHubChangeUsernameView(APIView):
    # Changing the username doesn't need update_session_auth_hash — Django's
    # session auth hash is derived from the password, not the username, and
    # the session itself keys off the user's pk, so the existing session
    # stays valid across a username change with no extra handling.
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ChangeUsernameSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({'detail': ['Username changed successfully.'], 'username': user.username})


class AdminHubChangePasswordView(APIView):
    # A regular DRF APIView (unlike AdminHubLoginAPIView) is fine here: the
    # request is already authenticated by the time this runs, so
    # SessionAuthentication.enforce_csrf() actually runs and CSRF is
    # correctly enforced — the gap that forced AdminHubLoginAPIView to stay
    # a plain Django View only applies to the anonymous login request.
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # Changing a user's password rotates their session auth hash, which
        # would otherwise log this same request's session out immediately.
        update_session_auth_hash(request, request.user)
        return Response({'detail': ['Password changed successfully.']})


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
