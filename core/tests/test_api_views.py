import pytest

pytestmark = pytest.mark.django_db


class TestAdminHubLoginAPIView:
    url = '/api/admin-hub/login/'

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
