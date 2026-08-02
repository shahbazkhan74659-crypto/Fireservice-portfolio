import re

import pytest
from django.core import mail
from django.core.cache import cache

pytestmark = pytest.mark.django_db

OTP_RE = re.compile(r'\b(\d{6})\b')


def _latest_otp():
    """Pulls the OTP straight out of the last sent email, same convention as
    core/tests/test_forgot_password.py's own helper — exercises the same
    path a real admin would rather than reaching into cache directly."""
    body = mail.outbox[-1].body
    match = OTP_RE.search(body)
    assert match, f'no 6-digit code found in email body: {body!r}'
    return match.group(1)


class TestAdminHubLoginAPIView:
    url = '/api/admin-hub/login/'

    @pytest.fixture(autouse=True)
    def _clear_login_lockout_cache(self):
        # Failure counters are keyed per-IP/per-username in the default
        # cache, and every Django test Client request shares the same
        # REMOTE_ADDR ('127.0.0.1') unless overridden — clear before and
        # after each test so counts from one test don't leak into the next.
        cache.clear()
        yield
        cache.clear()

    def test_valid_staff_credentials_log_in(self, client, staff_user):
        res = client.post(
            self.url,
            {'username': staff_user.username, 'password': 'pw12345!'},
            content_type='application/json',
        )
        assert res.status_code == 200
        assert '_auth_user_id' in client.session

    def test_wrong_password_rejected(self, client, staff_user):
        res = client.post(
            self.url,
            {'username': staff_user.username, 'password': 'definitely-wrong'},
            content_type='application/json',
        )
        assert res.status_code == 401
        assert '_auth_user_id' not in client.session

    def test_non_staff_user_rejected_with_same_status_as_wrong_password(self, client, regular_user):
        # Deliberately indistinguishable from a bad password (see the view's
        # own comment) — a login attempt shouldn't be able to enumerate
        # which usernames exist but merely lack Admin Hub access.
        res = client.post(
            self.url,
            {'username': regular_user.username, 'password': 'pw12345!'},
            content_type='application/json',
        )
        assert res.status_code == 401
        assert '_auth_user_id' not in client.session

    def test_missing_fields_rejected(self, client):
        res = client.post(self.url, {'username': 'someone'}, content_type='application/json')
        assert res.status_code == 400

    def test_malformed_json_rejected(self, client):
        res = client.post(self.url, data='not json', content_type='application/json')
        assert res.status_code == 400

    def test_lockout_after_repeated_failures_blocks_further_attempts(self, client, staff_user):
        for _ in range(5):
            res = client.post(
                self.url,
                {'username': staff_user.username, 'password': 'wrong'},
                content_type='application/json',
            )
            assert res.status_code == 401

        # 6th attempt is blocked by the lockout even with the *correct*
        # password — the point of a lockout is to stop further guesses, not
        # just to reject bad ones.
        res = client.post(
            self.url,
            {'username': staff_user.username, 'password': 'pw12345!'},
            content_type='application/json',
        )
        assert res.status_code == 429
        assert '_auth_user_id' not in client.session

    def test_successful_login_resets_failure_counter(self, client, staff_user):
        for _ in range(4):
            res = client.post(
                self.url,
                {'username': staff_user.username, 'password': 'wrong'},
                content_type='application/json',
            )
            assert res.status_code == 401

        res = client.post(
            self.url,
            {'username': staff_user.username, 'password': 'pw12345!'},
            content_type='application/json',
        )
        assert res.status_code == 200

        # A single wrong attempt right after logging back out is a normal
        # 401, not a 429 — proving the earlier near-lockout was cleared.
        client.logout()
        res = client.post(
            self.url,
            {'username': staff_user.username, 'password': 'wrong'},
            content_type='application/json',
        )
        assert res.status_code == 401

    def test_lockout_is_tracked_per_username_independent_of_ip(self, client, staff_user, regular_user):
        # Fail out staff_user's counter from one IP...
        for _ in range(5):
            res = client.post(
                self.url,
                {'username': staff_user.username, 'password': 'wrong'},
                content_type='application/json',
                REMOTE_ADDR='10.0.0.1',
            )
            assert res.status_code == 401

        # ...then confirm staff_user is locked out even from a different IP,
        # while a different username from that same fresh IP is unaffected.
        res = client.post(
            self.url,
            {'username': staff_user.username, 'password': 'pw12345!'},
            content_type='application/json',
            REMOTE_ADDR='10.0.0.2',
        )
        assert res.status_code == 429

        res = client.post(
            self.url,
            {'username': regular_user.username, 'password': 'pw12345!'},
            content_type='application/json',
            REMOTE_ADDR='10.0.0.2',
        )
        # regular_user is non-staff, so this is a normal 401 rejection, not
        # a 429 — proving the lockout above was scoped to staff_user, not a
        # blanket lockout of the whole cache.
        assert res.status_code == 401


class TestAdminHubChangeUsernameView:
    url = '/api/admin-hub/change-username/'

    def test_anonymous_rejected(self, client):
        res = client.post(self.url, {'new_username': 'newname'}, content_type='application/json')
        assert res.status_code in (401, 403)

    def test_non_staff_rejected(self, client, regular_user):
        client.force_login(regular_user)
        res = client.post(self.url, {'new_username': 'newname'}, content_type='application/json')
        assert res.status_code == 403

    def test_changes_username_and_keeps_session_alive(self, admin_client, staff_user):
        res = admin_client.post(self.url, {'new_username': 'shahbaz2'}, content_type='application/json')
        assert res.status_code == 200
        assert res.json()['username'] == 'shahbaz2'
        assert '_auth_user_id' in admin_client.session

        staff_user.refresh_from_db()
        assert staff_user.username == 'shahbaz2'

    def test_duplicate_username_rejected_case_insensitively(self, admin_client, staff_user, regular_user):
        res = admin_client.post(
            self.url, {'new_username': regular_user.username.upper()}, content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.username != regular_user.username.upper()

    def test_keeping_the_same_username_is_allowed(self, admin_client, staff_user):
        # Excludes the current user's own row from the uniqueness check, so
        # re-submitting the same name isn't treated as a duplicate of itself.
        res = admin_client.post(self.url, {'new_username': staff_user.username}, content_type='application/json')
        assert res.status_code == 200

    def test_invalid_characters_rejected(self, admin_client):
        # '!' isn't in the allowed set even though spaces now are (see the
        # test below) — this exercises rejection on a genuinely bad character.
        res = admin_client.post(self.url, {'new_username': 'bad-name!'}, content_type='application/json')
        assert res.status_code == 400

    def test_username_with_spaces_is_allowed(self, admin_client, staff_user):
        res = admin_client.post(self.url, {'new_username': 'Shahbaz Khan'}, content_type='application/json')
        assert res.status_code == 200
        staff_user.refresh_from_db()
        assert staff_user.username == 'Shahbaz Khan'


class TestAdminHubChangePasswordView:
    url = '/api/admin-hub/change-password/'

    def test_anonymous_rejected(self, client):
        res = client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'a-new-strong-pass'},
            content_type='application/json',
        )
        assert res.status_code in (401, 403)

    def test_non_staff_rejected(self, client, regular_user):
        client.force_login(regular_user)
        res = client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'a-new-strong-pass'},
            content_type='application/json',
        )
        assert res.status_code == 403

    def test_wrong_old_password_rejected_and_password_unchanged(self, admin_client, staff_user):
        res = admin_client.post(
            self.url,
            {'old_password': 'not-the-real-password', 'new_password': 'a-new-strong-pass'},
            content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_weak_new_password_rejected_via_django_validators(self, admin_client, staff_user):
        # Too short to satisfy AUTH_PASSWORD_VALIDATORS' MinimumLengthValidator,
        # proving the server enforces Django's real validators, not just the
        # frontend's lightweight length check.
        res = admin_client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'short'},
            content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_new_password_without_uppercase_rejected(self, admin_client, staff_user):
        res = admin_client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'no-upper-here1!'},
            content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_new_password_without_special_character_rejected(self, admin_client, staff_user):
        res = admin_client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'NoSpecialChar123'},
            content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_new_password_with_whitespace_rejected(self, admin_client, staff_user):
        res = admin_client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'Has A Space1!'},
            content_type='application/json',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.check_password('pw12345!')

    def test_correct_old_password_changes_it_and_keeps_session_alive(self, admin_client, staff_user):
        res = admin_client.post(
            self.url,
            {'old_password': 'pw12345!', 'new_password': 'A-New-Strong-Pass1!'},
            content_type='application/json',
        )
        assert res.status_code == 200
        # update_session_auth_hash should have kept this same session valid —
        # a protected page is still reachable without logging in again.
        assert '_auth_user_id' in admin_client.session

        staff_user.refresh_from_db()
        assert staff_user.check_password('A-New-Strong-Pass1!')
        assert not staff_user.check_password('pw12345!')


class TestAdminHubChangeEmailRequestOTPView:
    url = '/api/admin-hub/change-email/request-otp/'

    @pytest.fixture(autouse=True)
    def _clear_cache(self):
        cache.clear()
        mail.outbox.clear()
        yield
        cache.clear()

    def test_anonymous_rejected(self, client):
        res = client.post(self.url, {'new_email': 'new@example.com'}, content_type='application/json')
        assert res.status_code in (401, 403)
        assert len(mail.outbox) == 0

    def test_non_staff_rejected(self, client, regular_user):
        client.force_login(regular_user)
        res = client.post(self.url, {'new_email': 'new@example.com'}, content_type='application/json')
        assert res.status_code == 403
        assert len(mail.outbox) == 0

    def test_valid_new_email_sends_otp_to_new_address_not_current(self, admin_client, staff_user):
        res = admin_client.post(self.url, {'new_email': 'new-address@example.com'}, content_type='application/json')
        assert res.status_code == 200
        assert len(mail.outbox) == 1
        assert mail.outbox[0].to == ['new-address@example.com']
        assert _latest_otp()

    def test_same_as_current_email_rejected(self, admin_client, staff_user):
        res = admin_client.post(self.url, {'new_email': staff_user.email}, content_type='application/json')
        assert res.status_code == 400
        assert len(mail.outbox) == 0

    def test_email_already_used_by_another_staff_account_rejected(self, admin_client, django_user_model):
        django_user_model.objects.create_user('other', 'taken@example.com', 'pw12345!', is_staff=True)
        res = admin_client.post(self.url, {'new_email': 'taken@example.com'}, content_type='application/json')
        assert res.status_code == 400
        assert len(mail.outbox) == 0

    def test_malformed_email_rejected(self, admin_client):
        res = admin_client.post(self.url, {'new_email': 'not-an-email'}, content_type='application/json')
        assert res.status_code == 400
        assert len(mail.outbox) == 0

    def test_resend_within_cooldown_is_blocked(self, admin_client):
        res1 = admin_client.post(self.url, {'new_email': 'new-address@example.com'}, content_type='application/json')
        assert res1.status_code == 200

        res2 = admin_client.post(self.url, {'new_email': 'new-address@example.com'}, content_type='application/json')
        assert res2.status_code == 429
        assert len(mail.outbox) == 1


class TestAdminHubChangeEmailVerifyOTPView:
    REQUEST_URL = '/api/admin-hub/change-email/request-otp/'
    VERIFY_URL = '/api/admin-hub/change-email/verify/'
    NEW_EMAIL = 'new-address@example.com'

    @pytest.fixture(autouse=True)
    def _clear_cache(self):
        cache.clear()
        mail.outbox.clear()
        yield
        cache.clear()

    def test_anonymous_rejected(self, client):
        res = client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': '123456'}, content_type='application/json')
        assert res.status_code in (401, 403)

    def test_non_staff_rejected(self, client, regular_user):
        client.force_login(regular_user)
        res = client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': '123456'}, content_type='application/json')
        assert res.status_code == 403

    def test_correct_otp_saves_new_email_and_keeps_session_alive(self, admin_client, staff_user):
        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        otp = _latest_otp()

        res = admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': otp}, content_type='application/json')
        assert res.status_code == 200
        assert res.json()['email'] == self.NEW_EMAIL
        assert '_auth_user_id' in admin_client.session

        staff_user.refresh_from_db()
        assert staff_user.email == self.NEW_EMAIL

    def test_wrong_otp_rejected_and_email_unchanged(self, admin_client, staff_user):
        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        real_otp = _latest_otp()
        wrong_otp = '000000' if real_otp != '000000' else '111111'

        res = admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': wrong_otp}, content_type='application/json')
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.email != self.NEW_EMAIL

    def test_otp_is_single_use(self, admin_client):
        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        otp = _latest_otp()

        res1 = admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': otp}, content_type='application/json')
        assert res1.status_code == 200

        res2 = admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': otp}, content_type='application/json')
        assert res2.status_code == 400

    def test_otp_issued_for_a_different_email_is_rejected(self, admin_client):
        # Proves the cached OTP entry's own stored email is checked, not just
        # the code — an OTP sent to address A can't be replayed to confirm
        # address B even if the 6 digits happen to be typed correctly.
        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        otp = _latest_otp()

        res = admin_client.post(
            self.VERIFY_URL, {'new_email': 'someone-else@example.com', 'otp': otp}, content_type='application/json',
        )
        assert res.status_code == 400

    def test_no_otp_requested_yet_rejected(self, admin_client):
        res = admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': '123456'}, content_type='application/json')
        assert res.status_code == 400

    def test_five_wrong_attempts_invalidate_the_otp_even_with_correct_code_after(self, admin_client, staff_user):
        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        real_otp = _latest_otp()
        wrong_otp = '000000' if real_otp != '000000' else '111111'

        for i in range(5):
            res = admin_client.post(
                self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': wrong_otp}, content_type='application/json',
                REMOTE_ADDR=f'10.0.1.{i}',  # spread across IPs so only the OTP's own attempt cap kicks in
            )
            assert res.status_code == 400

        res = admin_client.post(
            self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': real_otp}, content_type='application/json',
            REMOTE_ADDR='10.0.1.99',
        )
        assert res.status_code == 400
        staff_user.refresh_from_db()
        assert staff_user.email != self.NEW_EMAIL

    def test_malformed_otp_rejected(self, admin_client):
        res = admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': 'abc'}, content_type='application/json')
        assert res.status_code == 400


class TestAdminHubChangeEmailRevertView:
    REQUEST_URL = '/api/admin-hub/change-email/request-otp/'
    VERIFY_URL = '/api/admin-hub/change-email/verify/'
    REVERT_URL = '/api/admin-hub/change-email/revert/'
    NEW_EMAIL = 'new-address@example.com'

    @pytest.fixture(autouse=True)
    def _clear_cache(self):
        cache.clear()
        mail.outbox.clear()
        yield
        cache.clear()

    def test_anonymous_rejected(self, client):
        res = client.post(self.REVERT_URL, {}, content_type='application/json')
        assert res.status_code in (401, 403)

    def test_non_staff_rejected(self, client, regular_user):
        client.force_login(regular_user)
        res = client.post(self.REVERT_URL, {}, content_type='application/json')
        assert res.status_code == 403

    def test_nothing_to_revert_is_a_harmless_no_op(self, admin_client, staff_user):
        original_email = staff_user.email
        res = admin_client.post(self.REVERT_URL, {}, content_type='application/json')
        assert res.status_code == 200
        staff_user.refresh_from_db()
        assert staff_user.email == original_email

    def test_revert_restores_the_previous_email_without_a_fresh_otp(self, admin_client, staff_user):
        original_email = staff_user.email

        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        otp = _latest_otp()
        admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': otp}, content_type='application/json')
        staff_user.refresh_from_db()
        assert staff_user.email == self.NEW_EMAIL

        res = admin_client.post(self.REVERT_URL, {}, content_type='application/json')
        assert res.status_code == 200
        assert res.json()['email'] == original_email
        staff_user.refresh_from_db()
        assert staff_user.email == original_email

    def test_revert_is_single_use(self, admin_client, staff_user):
        admin_client.post(self.REQUEST_URL, {'new_email': self.NEW_EMAIL}, content_type='application/json')
        otp = _latest_otp()
        admin_client.post(self.VERIFY_URL, {'new_email': self.NEW_EMAIL, 'otp': otp}, content_type='application/json')

        admin_client.post(self.REVERT_URL, {}, content_type='application/json')
        staff_user.refresh_from_db()
        reverted_email = staff_user.email

        # A second revert call has nothing left pending — it's a no-op, not
        # a further change (e.g. reverting a second time to some even older
        # value that doesn't exist).
        res = admin_client.post(self.REVERT_URL, {}, content_type='application/json')
        assert res.status_code == 200
        staff_user.refresh_from_db()
        assert staff_user.email == reverted_email


class TestBrandListCreateViewPermissions:
    """Brand stands in for every IsAdminUser-protected content endpoint —
    they all share the same permission_classes = [IsAdminUser] pattern."""

    url = '/api/admin-hub/brands/'

    def test_anonymous_rejected(self, client):
        res = client.get(self.url)
        assert res.status_code in (401, 403)

    def test_non_staff_authenticated_user_rejected(self, client, regular_user):
        client.force_login(regular_user)
        res = client.get(self.url)
        assert res.status_code == 403

    def test_staff_can_list(self, admin_client):
        res = admin_client.get(self.url)
        assert res.status_code == 200


class TestBrandOrderAutoIncrement:
    """perform_create()'s select_for_update()+aggregate(Max('order')) pattern
    is duplicated across seven endpoints (Brand/ClientLogo/Service/Product/
    ProcessPhase/Certification/FireRiskAssessmentItem) — Brand is the
    representative."""

    url = '/api/admin-hub/brands/'

    def test_order_increments_on_successive_creates(self, admin_client, make_png_upload):
        from website.models import Brand

        # Not 1/2: 0006_seed_brands.py data-migrates 5 real Brand rows into
        # every freshly-migrated database, test databases included — so a
        # brand-new environment never actually starts at an empty table.
        baseline = Brand.objects.count()

        res1 = admin_client.post(self.url, {'name': 'First', 'image': make_png_upload('a.png')})
        res2 = admin_client.post(self.url, {'name': 'Second', 'image': make_png_upload('b.png')})

        assert res1.status_code == 201
        assert res2.status_code == 201
        assert res1.json()['order'] == baseline + 1
        assert res2.json()['order'] == baseline + 2
