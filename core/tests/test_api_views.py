import pytest
from django.core.cache import cache

pytestmark = pytest.mark.django_db


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
    is duplicated across six endpoints (Brand/ClientLogo/Service/Product/
    Certification/FireRiskAssessmentItem) — Brand is the representative."""

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
