import pytest
from django.urls import reverse

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('url_name', [
    'home', 'about', 'clientele', 'services', 'process', 'brochure',
    'certifications', 'survey', 'contact', 'consultation',
])
def test_public_pages_return_200(client, url_name):
    res = client.get(reverse(url_name))
    assert res.status_code == 200


def test_csrf_cookie_set_on_a_form_hosting_page(client):
    # contact.html hosts the contact-form React island, which needs a
    # readable csrftoken cookie to set X-CSRFToken on its POST.
    res = client.get(reverse('contact'))
    assert 'csrftoken' in res.cookies


class TestAdminHubAccessControl:
    def test_anonymous_redirected_to_login(self, client):
        res = client.get(reverse('adminhub-home'))
        assert res.status_code == 302
        assert res.url.startswith(reverse('adminhub-login'))

    def test_non_staff_authenticated_user_redirected_to_login(self, client, regular_user):
        # A regular account must not reach Admin Hub just by being logged in
        # — StaffRequiredMixin's test_func() (is_staff) is what actually
        # blocks it. This used to 403 instead of redirecting: Django's
        # AccessMixin.handle_no_permission() (inherited by both
        # LoginRequiredMixin and UserPassesTestMixin) only redirects
        # *anonymous* visitors — an already-authenticated user who merely
        # fails test_func() got a raw PermissionDenied instead, contradicting
        # this mixin's own stated intent. Fixed with a handle_no_permission()
        # override in StaffRequiredMixin; this test pins the fixed behavior.
        client.force_login(regular_user)
        res = client.get(reverse('adminhub-home'))
        assert res.status_code == 302
        assert res.url.startswith(reverse('adminhub-login'))

    def test_staff_can_access(self, admin_client):
        res = admin_client.get(reverse('adminhub-home'))
        assert res.status_code == 200

    def test_logout_ends_the_session(self, admin_client):
        assert admin_client.get(reverse('adminhub-home')).status_code == 200
        admin_client.post(reverse('adminhub-logout'))
        res = admin_client.get(reverse('adminhub-home'))
        assert res.status_code == 302


class TestAdminHubHomeDashboardContext:
    """AdminHubHomeView.get_context_data() has real aggregation logic (lead
    counts, today-vs-30-day windows, peak-trend labeling, recent-activity
    ordering) worth testing directly rather than trusting it by inspection."""

    def test_recent_activity_shows_newest_leads_first_capped_at_five(self, admin_client):
        from datetime import timedelta

        from django.utils import timezone
        from leads.models import ContactMessage

        # created_at is auto_now_add, so it can't be set on create() —
        # staggering it after the fact keeps this test's intent (ordering +
        # the cap at 5) unambiguous regardless of the tiebreaker exercised
        # separately below.
        base = timezone.now()
        leads = [
            ContactMessage.objects.create(name=f'Lead {i}', phone='9876543210', email=f'lead{i}@example.com')
            for i in range(7)
        ]
        for i, lead in enumerate(leads):
            ContactMessage.objects.filter(pk=lead.pk).update(created_at=base + timedelta(seconds=i))

        res = admin_client.get(reverse('adminhub-home'))
        activity = res.context['recent_activity']

        assert len(activity) == 5
        assert activity[0]['name'] == 'Lead 6'  # most recently created
        assert [a['name'] for a in activity] == ['Lead 6', 'Lead 5', 'Lead 4', 'Lead 3', 'Lead 2']

    def test_recent_activity_breaks_same_timestamp_ties_by_pk(self, admin_client):
        # Regression test for a real gap the previous test's staggered
        # timestamps deliberately avoided exercising: leads created close
        # enough together to share a created_at value (plausible — datetime
        # resolution can be coarser than the gap between two rapid
        # submissions) used to sort in a DB-dependent, non-deterministic
        # order. AdminHubHomeView now breaks ties by -pk.
        from django.utils import timezone
        from leads.models import ContactMessage

        tied_at = timezone.now()
        leads = [
            ContactMessage.objects.create(name=f'Tied {i}', phone='9876543210', email=f'tied{i}@example.com')
            for i in range(3)
        ]
        ContactMessage.objects.filter(pk__in=[lead.pk for lead in leads]).update(created_at=tied_at)

        res = admin_client.get(reverse('adminhub-home'))
        names = [a['name'] for a in res.context['recent_activity']]

        # Highest pk (created last, even though the timestamp is identical)
        # sorts first.
        assert names[:3] == ['Tied 2', 'Tied 1', 'Tied 0']

    def test_todays_meter_counts_only_include_todays_leads(self, admin_client):
        from leads.models import SurveyRequest

        SurveyRequest.objects.create(
            name='Today Lead', email='today@example.com',
            address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
        )

        res = admin_client.get(reverse('adminhub-home'))
        meters = {m['label']: m for m in res.context['lead_meters']}

        assert meters['Survey Requests']['count'] == 1
        assert meters['Contact Messages']['count'] == 0

    def test_total_leads_sums_all_three_lead_types(self, admin_client):
        from leads.models import ConsultationRequest, ContactMessage, SurveyRequest

        SurveyRequest.objects.create(
            name='A', email='a@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
        )
        ContactMessage.objects.create(name='B', phone='9876543210', email='b@example.com')
        ConsultationRequest.objects.create(name='C', phone='9876543210')

        res = admin_client.get(reverse('adminhub-home'))
        assert res.context['total_leads'] == 3

    def test_site_setting_stats_reflect_saved_values(self, admin_client):
        from website.models import SiteSetting

        setting = SiteSetting.load()
        setting.years_experience = 42
        setting.save()

        res = admin_client.get(reverse('adminhub-home'))
        assert res.context['years_experience'] == 42

    def test_content_completeness_counts_only_populated_types(self, admin_client, make_png_upload):
        from website.models import Brand, Certification

        # Every CONTENT_MODELS type ships with a data-seed migration (see
        # website/migrations/0002.../0014...), so a fresh database already
        # has all 7 populated — emptying one type first is the only way to
        # exercise the "goes from unpopulated to populated" transition.
        Certification.objects.all().delete()

        res_before = admin_client.get(reverse('adminhub-home'))
        assert res_before.context['content_types_populated'] == 6

        Brand.objects.create(name='Second Brand Row', image=make_png_upload())
        res_still_six = admin_client.get(reverse('adminhub-home'))
        assert res_still_six.context['content_types_populated'] == 6  # Brand was already populated

        Certification.objects.create(
            name='Test Cert', description='Desc', meta='Meta', image=make_png_upload(),
        )
        res_after = admin_client.get(reverse('adminhub-home'))
        assert res_after.context['content_types_populated'] == 7
