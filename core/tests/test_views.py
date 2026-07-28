import pytest
from django.urls import reverse
from django.utils import timezone

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

    def test_recent_activity_shows_newest_leads_first_capped_at_three(self, admin_client):
        from datetime import timedelta

        from django.utils import timezone
        from leads.models import ContactMessage

        # created_at is auto_now_add, so it can't be set on create() —
        # staggering it after the fact keeps this test's intent (ordering +
        # the cap at 3) unambiguous regardless of the tiebreaker exercised
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

        assert len(activity) == 3
        assert activity[0]['name'] == 'Lead 6'  # most recently created
        assert [a['name'] for a in activity] == ['Lead 6', 'Lead 5', 'Lead 4']

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

    def test_resolved_leads_excluded_from_meters_total_and_recent_activity(self, admin_client):
        # The Dashboard is meant to reflect open (unresolved) leads only —
        # resolving a lead on the Leads page should immediately drop every
        # dashboard count, not just remove it from that page's own table.
        from leads.models import ContactMessage

        open_lead = ContactMessage.objects.create(name='Open Lead', phone='9876543210', email='open@example.com')
        ContactMessage.objects.create(
            name='Resolved Lead', phone='9876543210', email='resolved@example.com',
            resolved=True, resolved_at=timezone.now(),
        )

        res = admin_client.get(reverse('adminhub-home'))
        meters = {m['label']: m for m in res.context['lead_meters']}

        assert meters['Contact Messages']['count'] == 1
        assert res.context['total_leads'] == 1
        names = [a['name'] for a in res.context['recent_activity']]
        assert names == ['Open Lead']
        assert open_lead.name in names


class TestAdminHubLeadsPage:
    def test_unresolved_and_resolved_leads_land_in_separate_context_lists(self, admin_client):
        from leads.models import SurveyRequest

        open_lead = SurveyRequest.objects.create(
            name='Open', email='open@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
        )
        resolved_lead = SurveyRequest.objects.create(
            name='Resolved', email='resolved@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
            resolved=True, resolved_at=timezone.now(),
        )

        res = admin_client.get(reverse('adminhub-leads'))

        survey_names = [lead.name for lead in res.context['survey_requests']]
        assert survey_names == [open_lead.name]

        resolved_names = [lead['name'] for lead in res.context['resolved_requests']]
        assert resolved_names == [resolved_lead.name]


class TestAdminHubResolveLeadView:
    def test_resolving_a_lead_marks_it_resolved_and_responds_with_json(self, admin_client):
        # Called via fetch() from the Leads page's JS, not a real form
        # submission — a plain 200 JSON body, not a redirect, so the page
        # never navigates/reloads and the admin stays on whichever tab
        # they were working through.
        from leads.models import SurveyRequest

        lead = SurveyRequest.objects.create(
            name='To Resolve', email='resolve@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
        )

        res = admin_client.post(reverse('adminhub-leads-resolve', args=['survey', lead.pk]))

        lead.refresh_from_db()
        assert lead.resolved is True
        assert lead.resolved_at is not None
        assert res.status_code == 200
        assert res.json() == {'resolved': True}

    def test_unknown_lead_type_404s(self, admin_client):
        from leads.models import SurveyRequest

        lead = SurveyRequest.objects.create(
            name='X', email='x@example.com', address='123 Some Long Enough Street Address',
            problem='A problem description that is definitely long enough.',
            why_survey='A reason that is definitely long enough for validation.',
        )
        res = admin_client.post(reverse('adminhub-leads-resolve', args=['bogus-type', lead.pk]))
        assert res.status_code == 404

    def test_unknown_pk_404s(self, admin_client):
        res = admin_client.post(reverse('adminhub-leads-resolve', args=['survey', 999999]))
        assert res.status_code == 404

    def test_anonymous_redirected_to_login(self, client):
        res = client.post(reverse('adminhub-leads-resolve', args=['survey', 1]))
        assert res.status_code == 302
        assert res.url.startswith(reverse('adminhub-login'))

    def test_non_staff_redirected_to_login(self, client, regular_user):
        client.force_login(regular_user)
        res = client.post(reverse('adminhub-leads-resolve', args=['survey', 1]))
        assert res.status_code == 302
        assert res.url.startswith(reverse('adminhub-login'))
