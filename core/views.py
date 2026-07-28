import json
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from website.models import (
    Brand,
    Certification,
    ClientLogo,
    FireRiskAssessmentItem,
    MissionVisionItem,
    Product,
    Service,
    SiteSetting,
)

LEAD_MODELS = (
    ('Survey Requests', SurveyRequest, 'surveyrequest'),
    ('Contact Messages', ContactMessage, 'contactmessage'),
    ('Consultation Requests', ConsultationRequest, 'consultationrequest'),
)

CONTENT_MODELS = (
    MissionVisionItem, Service, FireRiskAssessmentItem,
    Product, ClientLogo, Brand, Certification,
)

TREND_DAYS = 30
CHART_W, CHART_H = 720, 160


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Gate for every authenticated Admin Hub page: being logged in isn't
    enough — the account must also be is_staff. Without this, any regular
    (non-staff) User account that successfully authenticates would get full
    Admin Hub access, since LoginRequiredMixin alone only checks
    is_authenticated. Intent is to redirect a logged-in-but-not-staff
    visitor to LOGIN_URL just like an anonymous one, rather than a 403 that
    would confirm the account exists and merely lacks permission — see
    handle_no_permission() below for why that needs a manual override
    rather than being AccessMixin's default behavior."""

    def test_func(self):
        return bool(self.request.user and self.request.user.is_staff)

    def handle_no_permission(self):
        # Django's AccessMixin.handle_no_permission() (inherited by both
        # LoginRequiredMixin and UserPassesTestMixin — confirmed by reading
        # Django 5.2's source directly, not assumed) only redirects
        # *anonymous* visitors to LOGIN_URL; an already-authenticated user
        # who merely fails test_func() gets `raise PermissionDenied` (a raw
        # 403) instead. That contradicted this class's own stated intent
        # above (a caught-by-test discrepancy, not a hypothetical one — see
        # core/tests/test_views.py). Overridden to always redirect instead.
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )


class RobotsTxtView(TemplateView):
    # Plain-text robots.txt — allows every public route, disallows Django's
    # own /admin/, the custom Admin Hub (/admin-hub/, already noindex'd via
    # adminhub/base.html's <meta name="robots"> tag, but crawlers should
    # ideally never even request it), and the API-only /api/ surface. The
    # Sitemap: line is built from the real request host rather than a
    # hardcoded domain, since no production domain is configured anywhere
    # in this project yet (ALLOWED_HOSTS is env-driven, currently empty).
    template_name = 'robots.txt'
    content_type = 'text/plain'


class HomeView(TemplateView):
    template_name = 'home.html'


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['mission_vision_items'] = MissionVisionItem.objects.all()
        return context


class ClienteleView(TemplateView):
    template_name = 'clientele.html'


class ProcessView(TemplateView):
    template_name = 'process.html'


class ServicesView(TemplateView):
    template_name = 'services.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        services = Service.objects.all()
        context['services'] = services
        context['fire_risk_items'] = FireRiskAssessmentItem.objects.all()

        # Service/hasOfferCatalog JSON-LD, built from the real Service rows
        # already looped in the page's own .grid--services (not fabricated
        # copy) — schema.org's guidance is hasOfferCatalog (not makesOffer,
        # which is for an Organization linking out to a catalog) when the
        # catalog is declared directly on a Service entity. Built with
        # json.dumps() rather than template-side {{ }} interpolation since
        # service.name/description are admin-editable free text (see
        # website.Service) that could contain quotes/ampersands Django's
        # HTML auto-escaping would otherwise corrupt inside a JSON string.
        origin = 'https' if self.request.is_secure() else 'http'
        origin = f'{origin}://{self.request.get_host()}'
        context['services_jsonld'] = json.dumps({
            '@context': 'https://schema.org',
            '@type': 'Service',
            'name': 'Fire & Life-Safety Systems',
            'provider': {
                '@type': 'LocalBusiness',
                'name': 'Iconic Techno Service',
                'url': f'{origin}/',
            },
            'areaServed': 'Silvassa',
            'hasOfferCatalog': {
                '@type': 'OfferCatalog',
                'name': 'Fire & Life-Safety Services',
                'itemListElement': [
                    {
                        '@type': 'Offer',
                        'itemOffered': {
                            '@type': 'Service',
                            'name': service.name,
                            'description': service.description,
                        },
                    }
                    for service in services
                ],
            },
        })
        return context


class BrochureView(TemplateView):
    template_name = 'brochure.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class CertificationsView(TemplateView):
    template_name = 'certifications.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class SurveyPageView(TemplateView):
    template_name = 'survey.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ContactPageView(TemplateView):
    template_name = 'contact.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class ConsultationView(TemplateView):
    template_name = 'consultation.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubLoginView(TemplateView):
    template_name = 'adminhub/login.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubHomeView(StaffRequiredMixin, TemplateView):
    # StaffRequiredMixin redirects to settings.LOGIN_URL ('/admin-hub/') with
    # a ?next= param when the visitor isn't authenticated or isn't staff.
    # ensure_csrf_cookie
    # is kept even though this page no longer hosts a form island itself,
    # since it's the first page hit after login and the cookie is cheap
    # insurance for whichever admin page the user clicks into next.
    template_name = 'adminhub/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = timezone.localdate()
        since = timezone.now() - timedelta(days=TREND_DAYS - 1)

        lead_counts = [(label, model.objects.count(), admin_name) for label, model, admin_name in LEAD_MODELS]
        total_leads = sum(count for _, count, _ in lead_counts)

        # Meter cards show today's leads (resets at local midnight, since
        # `today` is timezone.localdate()) rather than the all-time count —
        # the ring's fill share is likewise scoped to today's totals.
        today_counts = [
            (label, model.objects.filter(created_at__date=today).count())
            for label, model, _ in LEAD_MODELS
        ]
        total_today = sum(count for _, count in today_counts)
        last_30d_counts = {
            label: model.objects.filter(created_at__gte=since).count()
            for label, model, _ in LEAD_MODELS
        }

        context['lead_meters'] = [
            {
                'label': label,
                'count': count,
                'pct': round((count / total_today) * 100) if total_today else 0,
                'last_30d': last_30d_counts[label],
            }
            for label, count in today_counts
        ]
        context['total_leads'] = total_leads
        site_setting = SiteSetting.load()
        context['years_experience'] = site_setting.years_experience
        context['clients_served'] = site_setting.clients_served
        context['installations'] = site_setting.installations
        context['emergency_support'] = site_setting.emergency_support
        context['team_members'] = site_setting.team_members

        populated_types = sum(1 for model in CONTENT_MODELS if model.objects.exists())
        context['content_completeness_pct'] = round((populated_types / len(CONTENT_MODELS)) * 100)
        context['content_types_populated'] = populated_types
        context['content_types_total'] = len(CONTENT_MODELS)

        daily_counts = {}
        daily_by_type = {}
        for label, model, _ in LEAD_MODELS:
            rows = (
                model.objects.filter(created_at__gte=since)
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(n=Count('id'))
            )
            for row in rows:
                daily_counts[row['day']] = daily_counts.get(row['day'], 0) + row['n']
                daily_by_type.setdefault(row['day'], {})[label] = row['n']

        trend = [
            {'date': today - timedelta(days=i), 'count': daily_counts.get(today - timedelta(days=i), 0)}
            for i in range(TREND_DAYS - 1, -1, -1)
        ]
        raw_max = max((day['count'] for day in trend), default=0)
        trend_max = raw_max or 1
        # Label the most recent day that hit the peak — the "tip of the spike" —
        # directly on the chart, per the dataviz rule of labeling the extreme
        # rather than every point. No real peak (all-zero trend) gets no label.
        peak_index = None
        if raw_max > 0:
            for i, day in enumerate(trend):
                if day['count'] == raw_max:
                    peak_index = i

        n = len(trend)
        points = []
        for i, day in enumerate(trend):
            x = round(i * (CHART_W / (n - 1)), 1) if n > 1 else 0
            y = round(CHART_H - 10 - (day['count'] / trend_max) * (CHART_H - 20), 1)
            points.append({
                'x': x, 'y': y,
                'x_pct': round(x / CHART_W * 100, 2),
                'y_pct': round(y / CHART_H * 100, 2),
                'date': day['date'], 'count': day['count'], 'peak': i == peak_index,
            })

        path_d = 'M ' + ' L '.join(f"{p['x']},{p['y']}" for p in points)
        area_d = f"{path_d} L {points[-1]['x']},{CHART_H} L {points[0]['x']},{CHART_H} Z"

        context['lead_trend_points'] = points
        context['lead_trend_path'] = path_d
        context['lead_trend_area_path'] = area_d
        context['chart_w'] = CHART_W
        context['chart_h'] = CHART_H
        context['leads_last_7_days'] = sum(
            model.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
            for _, model, _ in LEAD_MODELS
        )

        # Detailed per-type daily breakdown for the table shown below the
        # dashboard — newest day first, unlike the chart's oldest-first trend.
        context['daily_breakdown'] = [
            {
                'date': today - timedelta(days=i),
                'survey': daily_by_type.get(today - timedelta(days=i), {}).get('Survey Requests', 0),
                'contact': daily_by_type.get(today - timedelta(days=i), {}).get('Contact Messages', 0),
                'consultation': daily_by_type.get(today - timedelta(days=i), {}).get('Consultation Requests', 0),
                'total': daily_counts.get(today - timedelta(days=i), 0),
            }
            for i in range(TREND_DAYS)
        ]

        activity = []
        for label, model, admin_name in LEAD_MODELS:
            # -pk tiebreaker (also applied to the final sort below) — without
            # one, leads created close enough together to share a created_at
            # value (plausible: auto_now_add's resolution can be coarser than
            # the gap between two near-simultaneous submissions) sort in a
            # DB-dependent, non-deterministic order. pk is a correct recency
            # proxy for a same-type tie (the realistic case — e.g. a batch
            # import); it's only a heuristic across two *different* lead
            # types tied at the same instant, since each model has its own
            # independent id sequence — an acceptable tradeoff for how rare
            # a genuine cross-type tie is versus no tiebreaker at all.
            for obj in model.objects.order_by('-created_at', '-pk')[:5]:
                activity.append({
                    'type': label[:-1] if label.endswith('s') else label,
                    'name': obj.name,
                    'created_at': obj.created_at,
                    'pk': obj.pk,
                    # Points at the Leads page's own row for this lead — the
                    # page switches to the matching tab and scrolls to that
                    # row (see leads.html's extra_scripts) instead of
                    # bouncing out to the raw Django admin change form.
                    'leads_url': f'/admin-hub/leads/#lead-{admin_name}-{obj.pk}',
                })
        activity.sort(key=lambda a: (a['created_at'], a['pk']), reverse=True)
        context['recent_activity'] = activity[:5]

        return context


class AdminHubLeadsView(StaffRequiredMixin, TemplateView):
    # Bare list view — no form/island, so no ensure_csrf_cookie needed.
    template_name = 'adminhub/leads.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['survey_requests'] = SurveyRequest.objects.all()
        context['contact_messages'] = ContactMessage.objects.all()
        context['consultation_requests'] = ConsultationRequest.objects.all()
        return context


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubClienteleView(StaffRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Client Logo management
    # React island, which POSTs/PATCHes/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/clientele.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubServicesView(StaffRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Services and Fire Risk
    # Assessment management React islands, which POST/PATCH/DELETE with an
    # X-CSRFToken header.
    template_name = 'adminhub/services.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubCertificationsView(StaffRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Certifications
    # management React island, which POSTs/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/certifications.html'
