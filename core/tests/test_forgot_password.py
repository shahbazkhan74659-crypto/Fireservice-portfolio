import re

import pytest
from django.core import mail
from django.core.cache import cache

pytestmark = pytest.mark.django_db

REQUEST_URL = '/api/admin-hub/forgot-password/request-otp/'
VERIFY_URL = '/api/admin-hub/forgot-password/verify-otp/'
RESET_URL = '/api/admin-hub/forgot-password/reset/'

OTP_RE = re.compile(r'\b(\d{6})\b')


def _latest_otp():
    """Pulls the OTP straight out of the last sent email rather than reaching
    into cache directly — exercises the same path a real admin would."""
    body = mail.outbox[-1].body
    match = OTP_RE.search(body)
    assert match, f'no 6-digit code found in email body: {body!r}'
    return match.group(1)


@pytest.fixture(autouse=True)
def _clear_cache():
    # Every rate-limit/OTP/reset-token key lives in the default cache, and
    # Django's test Client shares one REMOTE_ADDR across requests/tests
    # unless overridden — clear before and after each test.
    cache.clear()
    mail.outbox.clear()
    yield
    cache.clear()


class TestRequestOTPView:
    def test_valid_staff_email_sends_otp(self, client, staff_user):
        res = client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        assert res.status_code == 200
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == [staff_user.email]
        assert _latest_otp()

    def test_unregistered_email_rejected(self, client):
        res = client.post(REQUEST_URL, {'email': 'nobody@example.com'}, content_type='application/json')
        assert res.status_code == 400
        assert res.json()['detail'] == ['Enter Correct Email']
        assert len(mail.outbox) == 0

    def test_non_staff_email_rejected(self, client, regular_user):
        # Same reasoning as AdminHubLoginAPIView not distinguishing "wrong
        # password" from "not a staff account" — a non-staff account's own
        # email doesn't grant a password-reset code either.
        res = client.post(REQUEST_URL, {'email': regular_user.email}, content_type='application/json')
        assert res.status_code == 400
        assert len(mail.outbox) == 0

    def test_malformed_email_rejected(self, client):
        res = client.post(REQUEST_URL, {'email': 'not-an-email'}, content_type='application/json')
        assert res.status_code == 400
        assert len(mail.outbox) == 0

    def test_resend_within_cooldown_is_blocked(self, client, staff_user):
        res1 = client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        assert res1.status_code == 200

        res2 = client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        assert res2.status_code == 429
        assert len(mail.outbox) == 1

    def test_lockout_after_repeated_bad_emails(self, client):
        for _ in range(5):
            res = client.post(REQUEST_URL, {'email': 'nobody@example.com'}, content_type='application/json')
            assert res.status_code == 400

        res = client.post(REQUEST_URL, {'email': 'nobody@example.com'}, content_type='application/json')
        assert res.status_code == 429


class TestVerifyOTPView:
    def test_correct_otp_returns_reset_token(self, client, staff_user):
        client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        otp = _latest_otp()

        res = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': otp}, content_type='application/json')
        assert res.status_code == 200
        assert res.json()['reset_token']

    def test_wrong_otp_rejected(self, client, staff_user):
        client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        real_otp = _latest_otp()
        wrong_otp = '000000' if real_otp != '000000' else '111111'

        res = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': wrong_otp}, content_type='application/json')
        assert res.status_code == 400
        assert 'reset_token' not in res.json()

    def test_otp_is_single_use(self, client, staff_user):
        client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        otp = _latest_otp()

        res1 = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': otp}, content_type='application/json')
        assert res1.status_code == 200

        res2 = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': otp}, content_type='application/json')
        assert res2.status_code == 400

    def test_no_otp_requested_yet_rejected(self, client, staff_user):
        res = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': '123456'}, content_type='application/json')
        assert res.status_code == 400

    def test_five_wrong_attempts_invalidate_the_otp_even_with_correct_code_after(self, client, staff_user):
        client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        real_otp = _latest_otp()
        wrong_otp = '000000' if real_otp != '000000' else '111111'

        for i in range(5):
            res = client.post(
                VERIFY_URL, {'email': staff_user.email, 'otp': wrong_otp}, content_type='application/json',
                REMOTE_ADDR=f'10.0.0.{i}',  # spread across IPs so only the OTP's own attempt cap kicks in
            )
            assert res.status_code == 400

        # The OTP itself is now spent (too many wrong attempts), so even the
        # real code no longer works — must request a fresh one.
        res = client.post(
            VERIFY_URL, {'email': staff_user.email, 'otp': real_otp}, content_type='application/json',
            REMOTE_ADDR='10.0.0.99',
        )
        assert res.status_code == 400
        assert 'reset_token' not in res.json()

    def test_malformed_otp_rejected(self, client, staff_user):
        res = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': 'abc'}, content_type='application/json')
        assert res.status_code == 400


class TestResetView:
    def _get_reset_token(self, client, staff_user):
        client.post(REQUEST_URL, {'email': staff_user.email}, content_type='application/json')
        otp = _latest_otp()
        res = client.post(VERIFY_URL, {'email': staff_user.email, 'otp': otp}, content_type='application/json')
        return res.json()['reset_token']

    def test_valid_token_resets_password(self, client, staff_user):
        token = self._get_reset_token(client, staff_user)

        res = client.post(
            RESET_URL, {'reset_token': token, 'new_password': 'A-New-Strong-Pass1!'}, content_type='application/json',
        )
        assert res.status_code == 200

        staff_user.refresh_from_db()
        assert staff_user.check_password('A-New-Strong-Pass1!')
        assert not staff_user.check_password('pw12345!')

    def test_token_is_single_use(self, client, staff_user):
        token = self._get_reset_token(client, staff_user)

        res1 = client.post(
            RESET_URL, {'reset_token': token, 'new_password': 'A-New-Strong-Pass1!'}, content_type='application/json',
        )
        assert res1.status_code == 200

        res2 = client.post(
            RESET_URL, {'reset_token': token, 'new_password': 'Another-Strong-Pass2!'}, content_type='application/json',
        )
        assert res2.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('A-New-Strong-Pass1!')

    def test_invalid_token_rejected(self, client):
        res = client.post(
            RESET_URL, {'reset_token': 'not-a-real-token', 'new_password': 'A-New-Strong-Pass1!'},
            content_type='application/json',
        )
        assert res.status_code == 400

    def test_missing_token_rejected(self, client):
        res = client.post(RESET_URL, {'new_password': 'A-New-Strong-Pass1!'}, content_type='application/json')
        assert res.status_code == 400

    def test_weak_password_rejected_via_django_validators(self, client, staff_user):
        # Proves the real AUTH_PASSWORD_VALIDATORS run here too, not just on
        # the logged-in Change Password flow — same validators, same trust
        # boundary, different entry point.
        token = self._get_reset_token(client, staff_user)

        res = client.post(RESET_URL, {'reset_token': token, 'new_password': 'short'}, content_type='application/json')
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_password_without_uppercase_rejected(self, client, staff_user):
        token = self._get_reset_token(client, staff_user)

        res = client.post(
            RESET_URL, {'reset_token': token, 'new_password': 'no-upper-here1!'}, content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_reset_password_allows_login_with_new_credentials(self, client, staff_user):
        token = self._get_reset_token(client, staff_user)
        client.post(
            RESET_URL, {'reset_token': token, 'new_password': 'A-New-Strong-Pass1!'}, content_type='application/json',
        )

        res = client.post(
            '/api/admin-hub/login/',
            {'username': staff_user.username, 'password': 'A-New-Strong-Pass1!'},
            content_type='application/json',
        )
        assert res.status_code == 200
        assert '_auth_user_id' in client.session
