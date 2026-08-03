import json
import secrets

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, update_session_auth_hash
from django.core.cache import cache
from django.core.mail import send_mail
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

from core import rate_limit
from core.serializers import (
    ChangeEmailRequestSerializer,
    ChangeEmailVerifyOTPSerializer,
    ChangePasswordSerializer,
    ChangeUsernameSerializer,
    ForgotPasswordEmailSerializer,
    ForgotPasswordResetSerializer,
    ForgotPasswordVerifyOTPSerializer,
)
from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from leads.serializers import (
    ConsultationRequestSerializer,
    ContactMessageSerializer,
    SurveyRequestSerializer,
)
from website.models import Brand, Brochure, Certification, ClientLogo, FireRiskAssessmentItem, HeroSlide, MissionVisionItem, Product, ProcessPhase, Service, SiteSetting
from website.serializers import (
    BrandSerializer,
    BrochureSerializer,
    CertificationSerializer,
    ClientLogoSerializer,
    FireRiskAssessmentItemSerializer,
    HeroSlideSerializer,
    MissionVisionItemSerializer,
    ProcessPhaseSerializer,
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


def _parse_json_body(request):
    """Returns (data, error_response). Guards against both malformed JSON and
    a technically-valid-but-non-object body (e.g. a bare list/number), which
    would otherwise crash a later `data.get(...)`/serializer(data=data) call
    instead of failing cleanly with a 400."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return None, JsonResponse({'detail': ['Invalid request.']}, status=400)
    if not isinstance(data, dict):
        return None, JsonResponse({'detail': ['Invalid request.']}, status=400)
    return data, None


def _otp_email_body(otp):
    return f"""Dear Administrator,

We received a request to reset the password for your ICONIC TECHNO SERVICE admin account.

To proceed with the password reset, please use the following One-Time Password (OTP):

---

Admin Verification Code

OTP: {otp}

This verification code is valid for 5 minutes and can be used only once.

---

Important Security Notice

For the security of your administrative account:

- Do not share this OTP with anyone.
- ICONIC TECHNO SERVICE will never ask for your OTP through phone calls, SMS, or email.
- If you did not request a password reset, please ignore this email immediately and review your account activity.

This request was generated from the ICONIC TECHNO SERVICE Admin Panel. If the code expires before use, you can submit a new password reset request from the login page.

Maintaining the security of administrative access is critical to protecting website data, customer information, and system operations.

Thank you for helping us keep your account secure.

Best regards,

ICONIC TECHNO SERVICE
System Security Team
📧 iconictechnoservice.in@gmail.com
🌐 www.its.com

---

ICONIC TECHNO SERVICE
Admin Security • System Protection • Trusted Access

This is an automated security email. Please do not reply directly to this message."""


def _email_change_otp_body(otp, new_email):
    return f"""Dear Administrator,

We received a request to update the email address on your ICONIC TECHNO SERVICE admin account to {new_email}.

To confirm you own this address, please use the following One-Time Password (OTP):

---

Admin Verification Code

OTP: {otp}

This verification code is valid for 5 minutes and can be used only once.

---

Important Security Notice

For the security of your administrative account:

- Do not share this OTP with anyone.
- ICONIC TECHNO SERVICE will never ask for your OTP through phone calls, SMS, or email.
- If you did not request this change, please ignore this email and review your account activity.

This request was generated from the ICONIC TECHNO SERVICE Admin Panel. If the code expires before use, you can restart the email change from Account Settings.

Maintaining the security of administrative access is critical to protecting website data, customer information, and system operations.

Thank you for helping us keep your account secure.

Best regards,

ICONIC TECHNO SERVICE
System Security Team
📧 iconictechnoservice.in@gmail.com
🌐 www.its.com

---

ICONIC TECHNO SERVICE
Admin Security • System Protection • Trusted Access

This is an automated security email. Please do not reply directly to this message."""


class AdminHubForgotPasswordRequestOTPView(View):
    """Plain Django View, same CSRF reasoning as AdminHubLoginAPIView above —
    this runs before the admin is logged in, so a DRF APIView here would
    silently skip CSRF enforcement (see AdminHubLoginAPIView's own docstring
    for the full explanation).

    Also doubles as the "resend code" endpoint the OTP step calls — same URL,
    same cooldown/lockout rules apply to a resend as to the original request.

    The admin submits *their own* registered email (User.email), never the
    company's sending address — that address is only ever the "From" here.
    """

    OTP_TTL_SECONDS = 5 * 60
    RESEND_COOLDOWN_SECONDS = 60
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_WINDOW_SECONDS = 15 * 60

    def post(self, request):
        ip = rate_limit.client_ip(request)
        ip_key = f'adminhub_forgot_request:ip:{ip}' if ip else None

        data, error = _parse_json_body(request)
        if error:
            return error

        serializer = ForgotPasswordEmailSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        email = serializer.validated_data['email']
        email_key = f'adminhub_forgot_request:email:{email.lower()}'

        if rate_limit.is_locked_out(ip_key, email_key, threshold=self.LOCKOUT_THRESHOLD):
            return JsonResponse(
                {'detail': ['Too many requests. Please try again in a few minutes.']}, status=429,
            )

        User = get_user_model()
        user = User.objects.filter(is_staff=True, email__iexact=email).first()
        if user is None:
            # Recorded on both counters like a login failure — an anonymous
            # visitor otherwise has an unlimited-attempts oracle for guessing
            # which email addresses are registered admin accounts.
            rate_limit.record_failure(ip_key, self.LOCKOUT_WINDOW_SECONDS)
            rate_limit.record_failure(email_key, self.LOCKOUT_WINDOW_SECONDS)
            return JsonResponse({'detail': ['Enter Correct Email']}, status=400)

        cooldown_key = f'adminhub_forgot_cooldown:{user.pk}'
        if cache.get(cooldown_key):
            return JsonResponse(
                {'detail': ['Please wait a minute before requesting another code.']}, status=429,
            )

        otp = f'{secrets.randbelow(1_000_000):06d}'
        cache.set(f'adminhub_forgot_otp:{user.pk}', {'otp': otp, 'attempts': 0}, self.OTP_TTL_SECONDS)
        cache.set(cooldown_key, True, self.RESEND_COOLDOWN_SECONDS)

        send_mail(
            'ICONIC TECHNO SERVICE — Admin Password Reset OTP',
            _otp_email_body(otp),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return JsonResponse({'detail': ['A verification code has been sent to your email.']})


class AdminHubForgotPasswordVerifyOTPView(View):
    """Plain Django View — same CSRF reasoning as the request-OTP view above."""

    OTP_TTL_SECONDS = 5 * 60  # must match AdminHubForgotPasswordRequestOTPView's own TTL
    OTP_MAX_ATTEMPTS = 5
    RESET_TOKEN_TTL_SECONDS = 10 * 60
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_WINDOW_SECONDS = 5 * 60

    def post(self, request):
        ip = rate_limit.client_ip(request)
        ip_key = f'adminhub_forgot_verify:ip:{ip}' if ip else None

        data, error = _parse_json_body(request)
        if error:
            return error

        serializer = ForgotPasswordVerifyOTPSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)
        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']

        if rate_limit.is_locked_out(ip_key, threshold=self.LOCKOUT_THRESHOLD):
            return JsonResponse(
                {'detail': ['Too many attempts. Please request a new code and try again later.']}, status=429,
            )

        User = get_user_model()
        user = User.objects.filter(is_staff=True, email__iexact=email).first()
        if user is None:
            rate_limit.record_failure(ip_key, self.LOCKOUT_WINDOW_SECONDS)
            return JsonResponse({'detail': ['Enter Correct Email']}, status=400)

        otp_key = f'adminhub_forgot_otp:{user.pk}'
        entry = cache.get(otp_key)
        if entry is None:
            return JsonResponse({'detail': ['This code has expired. Please request a new one.']}, status=400)

        if entry['otp'] != otp:
            rate_limit.record_failure(ip_key, self.LOCKOUT_WINDOW_SECONDS)
            entry['attempts'] += 1
            if entry['attempts'] >= self.OTP_MAX_ATTEMPTS:
                cache.delete(otp_key)
                return JsonResponse(
                    {'detail': ['Too many incorrect attempts. Please request a new code.']}, status=400,
                )
            cache.set(otp_key, entry, self.OTP_TTL_SECONDS)
            return JsonResponse({'detail': ['Incorrect code.']}, status=400)

        # OTP is single-use — consumed as soon as it's checked correctly, so
        # it can't be replayed to mint a second reset token.
        cache.delete(otp_key)
        if ip_key:
            cache.delete(ip_key)

        reset_token = secrets.token_urlsafe(32)
        cache.set(f'adminhub_forgot_reset_token:{reset_token}', user.pk, self.RESET_TOKEN_TTL_SECONDS)

        return JsonResponse({'detail': ['Code verified.'], 'reset_token': reset_token})


class AdminHubForgotPasswordResetView(View):
    """Plain Django View — same CSRF reasoning as the two views above.

    No rate-limiting of its own: the reset_token is a 256-bit
    secrets.token_urlsafe value handed out only after a correct OTP, so
    guessing one directly isn't a realistic attack the way a 6-digit OTP or a
    password is — the OTP step above is what's actually guarded against
    brute force.
    """

    def post(self, request):
        data, error = _parse_json_body(request)
        if error:
            return error

        reset_token = (data.get('reset_token') or '').strip()
        token_key = f'adminhub_forgot_reset_token:{reset_token}'
        user_pk = cache.get(token_key) if reset_token else None
        if user_pk is None:
            return JsonResponse(
                {'detail': ['This reset link has expired. Please start again.']}, status=400,
            )

        User = get_user_model()
        try:
            user = User.objects.get(pk=user_pk, is_staff=True)
        except User.DoesNotExist:
            cache.delete(token_key)
            return JsonResponse(
                {'detail': ['This reset link has expired. Please start again.']}, status=400,
            )

        serializer = ForgotPasswordResetSerializer(data=data, context={'user': user})
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        user.set_password(serializer.validated_data['new_password'])
        user.save(update_fields=['password'])
        # Single-use: a spent or abandoned token can't be replayed.
        cache.delete(token_key)

        return JsonResponse({'detail': ['Password reset successful. Please log in with your new password.']})


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


class AdminHubChangeEmailRequestOTPView(APIView):
    """Step 1 of Account Settings' "Change Email": sends a 6-digit OTP to the
    *new* address the admin typed (not their current registered email) to
    prove they actually control it before it's ever saved. A regular DRF
    APIView is fine here (unlike the anonymous Forgot Password/Login views
    above) — the request is already authenticated by the time this runs, so
    SessionAuthentication.enforce_csrf() actually runs and CSRF is correctly
    enforced (same reasoning as AdminHubChangePasswordView).

    Also doubles as the "resend code" endpoint — same URL, same cooldown
    applies to a resend as to the original request, mirroring
    AdminHubForgotPasswordRequestOTPView's own convention.
    """

    permission_classes = [IsAdminUser]

    OTP_TTL_SECONDS = 5 * 60  # must match AdminHubChangeEmailVerifyOTPView's own TTL
    RESEND_COOLDOWN_SECONDS = 60
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_WINDOW_SECONDS = 15 * 60

    def post(self, request):
        serializer = ChangeEmailRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data['new_email']

        user = request.user
        ip_key = f'adminhub_email_change_request:ip:{rate_limit.client_ip(request)}'
        user_key = f'adminhub_email_change_request:user:{user.pk}'
        if rate_limit.is_locked_out(ip_key, user_key, threshold=self.LOCKOUT_THRESHOLD):
            return Response(
                {'detail': ['Too many requests. Please try again in a few minutes.']}, status=429,
            )

        cooldown_key = f'adminhub_email_change_cooldown:{user.pk}'
        if cache.get(cooldown_key):
            return Response(
                {'detail': ['Please wait a minute before requesting another code.']}, status=429,
            )

        otp = f'{secrets.randbelow(1_000_000):06d}'
        # Keyed by user pk (not the new email) and stores the target email
        # alongside the code, so verify can confirm the OTP was actually
        # issued for the address being submitted, not a stale one left over
        # from an earlier attempt with a different address.
        cache.set(
            f'adminhub_email_change_otp:{user.pk}',
            {'otp': otp, 'attempts': 0, 'email': new_email},
            self.OTP_TTL_SECONDS,
        )
        cache.set(cooldown_key, True, self.RESEND_COOLDOWN_SECONDS)

        send_mail(
            'ICONIC TECHNO SERVICE — Confirm Your New Admin Email',
            _email_change_otp_body(otp, new_email),
            settings.DEFAULT_FROM_EMAIL,
            [new_email],
            fail_silently=False,
        )

        return Response({'detail': ['A verification code has been sent to the new email address.']})


class AdminHubChangeEmailVerifyOTPView(APIView):
    """Step 2 — a correct OTP against the *new* email is what actually saves
    it onto the user's account; there's no separate save step after this
    succeeds, matching how the checkbox's green tick is meant to mean
    "confirmed and already saved," not just "verified, now click Save."

    The address being replaced is stashed in the cache for REVERT_TTL_SECONDS
    so Account Settings' Cancel button — or closing the modal any way other
    than Done — can restore it via AdminHubChangeEmailRevertView without
    needing a second OTP round-trip to the *old* address just to undo
    something that was never meant to be final yet."""

    permission_classes = [IsAdminUser]

    OTP_TTL_SECONDS = 5 * 60  # must match AdminHubChangeEmailRequestOTPView's own TTL
    OTP_MAX_ATTEMPTS = 5
    LOCKOUT_THRESHOLD = 5
    LOCKOUT_WINDOW_SECONDS = 5 * 60
    REVERT_TTL_SECONDS = 30 * 60  # generous window covering a realistic Account Settings session

    def post(self, request):
        serializer = ChangeEmailVerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        new_email = serializer.validated_data['new_email']
        otp = serializer.validated_data['otp']

        user = request.user
        ip_key = f'adminhub_email_change_verify:ip:{rate_limit.client_ip(request)}'
        if rate_limit.is_locked_out(ip_key, threshold=self.LOCKOUT_THRESHOLD):
            return Response(
                {'detail': ['Too many attempts. Please request a new code and try again later.']}, status=429,
            )

        otp_key = f'adminhub_email_change_otp:{user.pk}'
        entry = cache.get(otp_key)
        if entry is None:
            return Response({'detail': ['This code has expired. Please request a new one.']}, status=400)

        if entry['email'].lower() != new_email.lower() or entry['otp'] != otp:
            rate_limit.record_failure(ip_key, self.LOCKOUT_WINDOW_SECONDS)
            entry['attempts'] += 1
            if entry['attempts'] >= self.OTP_MAX_ATTEMPTS:
                cache.delete(otp_key)
                return Response(
                    {'detail': ['Too many incorrect attempts. Please request a new code.']}, status=400,
                )
            cache.set(otp_key, entry, self.OTP_TTL_SECONDS)
            return Response({'detail': ['Incorrect code.']}, status=400)

        # OTP is single-use — consumed as soon as it's checked correctly, so
        # it can't be replayed to reconfirm/overwrite the email a second time.
        cache.delete(otp_key)
        rate_limit.clear(ip_key)

        # Stashed before overwriting so a same-session Cancel can restore it
        # (see AdminHubChangeEmailRevertView) — each successful verify
        # overwrites this with whatever was active immediately before it, so
        # an abandoned session's stale key is harmless: it's only ever read
        # by a revert call the frontend gates on "did this session's Email
        # section actually run"; it doesn't reappear as a live email value on
        # its own.
        cache.set(f'adminhub_email_revert:{user.pk}', user.email, self.REVERT_TTL_SECONDS)

        user.email = new_email
        user.save(update_fields=['email'])

        return Response({'detail': ['Email confirmed and updated.'], 'email': user.email})


class AdminHubChangeEmailRevertView(APIView):
    """Restores whatever email AdminHubChangeEmailVerifyOTPView most recently
    overwrote for this user, without requiring a fresh OTP — reverting to an
    address that was already the account's own confirmed email needs no new
    proof of ownership. Only ever called by the frontend when Account
    Settings' Cancel button (or closing the modal any other way) is used
    after the Email section actually changed something this session; if
    nothing did, there's no pending key and this is a harmless no-op."""

    permission_classes = [IsAdminUser]

    def post(self, request):
        user = request.user
        key = f'adminhub_email_revert:{user.pk}'
        previous_email = cache.get(key)
        if previous_email is None:
            return Response({'detail': ['Nothing to revert.']})

        user.email = previous_email
        user.save(update_fields=['email'])
        cache.delete(key)

        return Response({'detail': ['Email change reverted.'], 'email': user.email})


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


class ProcessPhaseListCreateView(ListCreateAPIView):
    queryset = ProcessPhase.objects.all()
    serializer_class = ProcessPhaseSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (ProcessPhase.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class ProcessPhaseDetailView(RetrieveUpdateDestroyAPIView):
    queryset = ProcessPhase.objects.all()
    serializer_class = ProcessPhaseSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]


class HeroSlideListCreateView(ListCreateAPIView):
    queryset = HeroSlide.objects.all()
    serializer_class = HeroSlideSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        with transaction.atomic():
            next_order = (HeroSlide.objects.select_for_update().aggregate(Max('order'))['order__max'] or 0) + 1
            serializer.save(order=next_order)


class HeroSlideDeleteView(DestroyAPIView):
    # DestroyAPIView only, not RetrieveUpdateDestroyAPIView — a slide is
    # swapped by deleting and re-adding, no Edit exposed, same as
    # Certification.
    queryset = HeroSlide.objects.all()
    serializer_class = HeroSlideSerializer
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


class BrochureDetailView(RetrieveUpdateAPIView):
    # Singleton, same pattern as SiteSettingDetailView — get_object always
    # resolves to the one pk=1 row rather than a URL pk.
    serializer_class = BrochureSerializer
    parser_classes = [MultiPartParser, FormParser]  # uploads arrive as multipart, not JSON
    permission_classes = [IsAdminUser]

    def get_object(self):
        return Brochure.load()
