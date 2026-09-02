import calendar
import json
from datetime import date, datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import TemplateView

from core.locations import get_location
from leads.models import ConsultationRequest, ContactMessage, SurveyRequest
from leads.services import RESOLVED_LEAD_RETENTION_DAYS, purge_resolved_leads
from website.models import (
    BlogPost,
    Brochure,
    Certification,
    ClientLogo,
    FireRiskAssessmentItem,
    MissionVisionItem,
    Product,
    ProcessPhase,
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
    Product, ClientLogo, Certification,
)

TREND_DAYS = 30
CHART_W, CHART_H = 720, 160


def _shift_month(first_of_month, delta):
    """Return the first-of-month date `delta` calendar months away from
    `first_of_month` (also assumed to already be a first-of-month date)."""
    month_index = first_of_month.month - 1 + delta
    year = first_of_month.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # process.html loops over these in order — every phase's content
        # (image, title, tagline, both cards) is DB-driven, so adding or
        # removing a row changes how many phases render, no template edits.
        context['process_phases'] = ProcessPhase.objects.all()
        return context


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


def _service_page_breadcrumb_jsonld(request, service_name):
    """Shared by every fixed per-service page below — a 3-level breadcrumb
    (Home > Services > {service_name}) that the sitewide 2-level
    breadcrumb_jsonld in core/context_processors.py can't produce. Same
    reasoning as BlogDetailView.blog_breadcrumb_jsonld: rendered under its
    own context key from each page's own extra_head block, and none of
    these url names are added to BREADCRUMB_NAMES, so the sitewide
    processor stays silent on these pages and there's no duplicate/
    conflicting BreadcrumbList JSON-LD."""
    origin = 'https' if request.is_secure() else 'http'
    origin = f'{origin}://{request.get_host()}'
    return json.dumps({
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{origin}/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Services', 'item': f'{origin}/services/'},
            {'@type': 'ListItem', 'position': 3, 'name': service_name, 'item': f'{origin}{request.path}'},
        ],
    })


class FireAlarmSystemView(TemplateView):
    template_name = 'service-fire-alarm-system.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Fire Alarm System').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Fire Alarm System')
        return context


class GasDetectionSystemView(TemplateView):
    template_name = 'service-gas-detection-system.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Gas Detection System').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Gas Detection System')
        return context


class GasSuppressionSystemView(TemplateView):
    template_name = 'service-gas-suppression-system.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Gas Suppression System').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Gas Suppression System')
        return context


class HvwsMvwsSystemView(TemplateView):
    template_name = 'service-hvws-mvws-system.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='HVWS / MVWS System').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'HVWS / MVWS System')
        return context


class FireExtinguishersView(TemplateView):
    template_name = 'service-fire-extinguishers.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Fire Extinguishers').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Fire Extinguishers')
        return context


class SafetyEquipmentView(TemplateView):
    template_name = 'service-safety-equipment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Safety Equipment').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Safety Equipment')
        return context


class FirePumpHouseView(TemplateView):
    template_name = 'service-fire-pump-house.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Fire Pump House').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Fire Pump House')
        return context


class FireHydrantSystemView(TemplateView):
    template_name = 'service-fire-hydrant-system.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='Fire Hydrant System').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'Fire Hydrant System')
        return context


class PavaSystemView(TemplateView):
    template_name = 'service-pava-system.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = Service.objects.filter(name='PAVA System').first()
        context['service_breadcrumb_jsonld'] = _service_page_breadcrumb_jsonld(self.request, 'PAVA System')
        return context


class LocationView(TemplateView):
    # One parametrized view backing all 4 corridor-town landing pages (see
    # core/locations.py) rather than 4 near-duplicate view classes — the 4
    # pages share ~90% identical structure (same 8 real Service rows, same
    # credential block, same CTA, same map, same JSON-LD shape except
    # areaServed), only H1/intro/meta/slug vary per town. Same reasoning as
    # BlogDetailView being one view handling many posts, not one per post.
    template_name = 'location.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = get_location(kwargs['slug'])
        if location is None:
            raise Http404
        context['location'] = location
        context['services'] = Service.objects.all()

        # Service JSON-LD with areaServed set to this specific town — same
        # pattern ServicesView already uses (see services_jsonld there),
        # extended per the Technical-Architect's own recommendation that
        # areaServed should eventually cover the corridor towns, not just
        # 'Silvassa'. Built with json.dumps() for the same admin-editable-
        # free-text reason ServicesView's own JSON-LD is.
        origin = 'https' if self.request.is_secure() else 'http'
        origin = f'{origin}://{self.request.get_host()}'
        context['location_jsonld'] = json.dumps({
            '@context': 'https://schema.org',
            '@type': 'Service',
            'name': 'Fire & Life-Safety Systems',
            'provider': {
                '@type': 'LocalBusiness',
                'name': 'Iconic Techno Service',
                'url': f'{origin}/',
            },
            'areaServed': location['town'],
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
                    for service in context['services']
                ],
            },
        })

        # Per-town 3-level breadcrumb (Home > {Town} Fire Safety > ...) —
        # same reasoning as BlogDetailView's blog_breadcrumb_jsonld: these 4
        # pages all share one url_name ('location'), so the sitewide
        # BREADCRUMB_NAMES dict (keyed by url_name, one static label per
        # name) structurally can't distinguish between them. Rendered under
        # a distinct context key from this template's own extra_head block,
        # not added to BREADCRUMB_NAMES at all — same pattern, same reason.
        context['location_breadcrumb_jsonld'] = json.dumps({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{origin}/'},
                {'@type': 'ListItem', 'position': 2, 'name': location['h1'], 'item': f'{origin}{self.request.path}'},
            ],
        })
        return context


class BlogListView(TemplateView):
    template_name = 'blog-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts = BlogPost.objects.filter(is_published=True)
        paginator = Paginator(posts, 9)
        page_number = self.request.GET.get('page')
        context['page_obj'] = paginator.get_page(page_number)
        return context


class BlogDetailView(TemplateView):
    template_name = 'blog-detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_or_404(BlogPost, slug=kwargs['slug'], is_published=True)
        context['post'] = post
        context['meta_description_override'] = post.meta_description or post.excerpt

        # Per-post 3-level breadcrumb (Home > Blog > {post.title}) — the
        # sitewide breadcrumb_jsonld in core/context_processors.py is a
        # static 2-level dict lookup keyed by url_name and structurally
        # cannot produce a per-object dynamic title. Rendered under a
        # distinct context key (not `breadcrumb_jsonld`) and only from this
        # template's own extra_head block, deliberately avoiding any
        # same-key collision with the context processor's value — 'blog-
        # detail' is intentionally NOT added to BREADCRUMB_NAMES, so the
        # sitewide processor naturally emits nothing for this page's
        # url_name and there's no duplicate/conflicting BreadcrumbList
        # JSON-LD on the same page.
        origin = 'https' if self.request.is_secure() else 'http'
        origin = f'{origin}://{self.request.get_host()}'
        context['blog_breadcrumb_jsonld'] = json.dumps({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{origin}/'},
                {'@type': 'ListItem', 'position': 2, 'name': 'Blog', 'item': f'{origin}/blog/'},
                {'@type': 'ListItem', 'position': 3, 'name': post.title, 'item': f'{origin}{self.request.path}'},
            ],
        })
        return context


class BrochureView(TemplateView):
    template_name = 'brochure.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brochure'] = Brochure.load()
        return context


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

        # The whole dashboard reflects *open* (unresolved) leads only — once
        # a lead is marked resolved on the Leads page it moves to that
        # page's Resolved Requests tab and every count here (meters, totals,
        # trend, recent activity) drops accordingly, rather than staying a
        # permanent historical tally.
        lead_counts = [
            (label, model.objects.filter(resolved=False).count(), admin_name)
            for label, model, admin_name in LEAD_MODELS
        ]
        total_leads = sum(count for _, count, _ in lead_counts)

        # Meter cards show today's leads (resets at local midnight, since
        # `today` is timezone.localdate()) rather than the all-time count.
        # The ring itself is just a count display, not a ratio of anything
        # (there's no natural "out of X" denominator for a raw count), so
        # it's always rendered as a full ring regardless of the count —
        # unlike Content Completeness below, which is a genuine fraction.
        today_counts = [
            (label, model.objects.filter(created_at__date=today, resolved=False).count())
            for label, model, _ in LEAD_MODELS
        ]
        last_30d_counts = {
            label: model.objects.filter(created_at__gte=since, resolved=False).count()
            for label, model, _ in LEAD_MODELS
        }

        context['lead_meters'] = [
            {
                'label': label,
                'count': count,
                'pct': 100,
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
        context['hero_slide_duration'] = site_setting.hero_slide_duration_seconds
        context['lead_notification_threshold'] = site_setting.lead_notification_threshold
        context['brochure'] = Brochure.load()

        populated_types = sum(1 for model in CONTENT_MODELS if model.objects.exists())
        context['content_completeness_pct'] = round((populated_types / len(CONTENT_MODELS)) * 100)
        context['content_types_populated'] = populated_types
        context['content_types_total'] = len(CONTENT_MODELS)

        daily_counts = {}
        daily_by_type = {}
        for label, model, _ in LEAD_MODELS:
            rows = (
                model.objects.filter(created_at__gte=since, resolved=False)
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
            model.objects.filter(created_at__gte=timezone.now() - timedelta(days=7), resolved=False).count()
            for _, model, _ in LEAD_MODELS
        )

        # Detailed per-type daily breakdown for the table shown below the
        # dashboard — newest day first, unlike the chart's oldest-first trend.
        # Unlike the chart/meters above (always a fixed trailing 30-day
        # window), this table is paginated by real calendar month via a
        # ?month=YYYY-MM query param, so older leads aren't stuck outside any
        # viewable window — the Previous/Next arrows below the table just
        # link to this same page with a different month.
        current_month_start = today.replace(day=1)
        try:
            selected_month_start = datetime.strptime(
                self.request.GET.get('month', ''), '%Y-%m'
            ).date().replace(day=1)
        except ValueError:
            selected_month_start = current_month_start
        # A future month has nothing to show and would break the "Next only
        # appears once you've gone back" rule below — clamp rather than 404,
        # since this only happens from a hand-edited URL.
        if selected_month_start > current_month_start:
            selected_month_start = current_month_start

        days_in_selected_month = calendar.monthrange(selected_month_start.year, selected_month_start.month)[1]
        month_end = selected_month_start.replace(day=days_in_selected_month)
        # Don't list days that haven't happened yet when the selected month
        # is the current one.
        last_visible_day = min(month_end, today)

        month_daily_counts = {}
        month_daily_by_type = {}
        for label, model, _ in LEAD_MODELS:
            rows = (
                model.objects.filter(
                    created_at__date__gte=selected_month_start,
                    created_at__date__lte=last_visible_day,
                    resolved=False,
                )
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(n=Count('id'))
            )
            for row in rows:
                month_daily_counts[row['day']] = month_daily_counts.get(row['day'], 0) + row['n']
                month_daily_by_type.setdefault(row['day'], {})[label] = row['n']

        days_span = (last_visible_day - selected_month_start).days + 1
        context['daily_breakdown'] = [
            {
                'date': last_visible_day - timedelta(days=i),
                'survey': month_daily_by_type.get(last_visible_day - timedelta(days=i), {}).get('Survey Requests', 0),
                'contact': month_daily_by_type.get(last_visible_day - timedelta(days=i), {}).get('Contact Messages', 0),
                'consultation': month_daily_by_type.get(last_visible_day - timedelta(days=i), {}).get('Consultation Requests', 0),
                'total': month_daily_counts.get(last_visible_day - timedelta(days=i), 0),
            }
            for i in range(days_span)
        ]
        context['breakdown_month_label'] = selected_month_start.strftime('%B %Y')
        # Left/Previous has no lower bound and is always shown, regardless of
        # whether that month turns out to have any leads in it — the table's
        # own empty state covers that case. Right/Next is only ever shown
        # once the admin has navigated to a month before the current one,
        # since there's nothing meaningful to view ahead of "now".
        context['breakdown_prev_month'] = _shift_month(selected_month_start, -1).strftime('%Y-%m')
        context['breakdown_next_month'] = (
            _shift_month(selected_month_start, 1).strftime('%Y-%m')
            if selected_month_start < current_month_start else None
        )

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
            for obj in model.objects.filter(resolved=False).order_by('-created_at', '-pk')[:3]:
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
        context['recent_activity'] = activity[:3]

        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # The Previous/Next month buttons on the daily-breakdown table
        # fetch() this same URL (?month=YYYY-MM) rather than doing a full
        # page navigation, so the change can fade in smoothly instead of a
        # hard reload — see breakdown-table.html's inline script. Reusing
        # the full get_context_data() (rather than splitting out a
        # cheaper month-only path) keeps this view's context-building in
        # one place; the extra dashboard-wide queries are inexpensive and
        # this is low-traffic, staff-only usage, not worth the added
        # complexity of a second, leaner context method.
        if request.headers.get('X-Requested-With') == 'fetch':
            return render(request, 'adminhub/breakdown-table.html', context)
        return self.render_to_response(context)


class AdminHubLeadsView(StaffRequiredMixin, TemplateView):
    # Bare list view — no form/island, so no ensure_csrf_cookie needed (the
    # resolve action's {% csrf_token %} tag triggers the cookie itself).
    template_name = 'adminhub/leads.html'

    def get_context_data(self, **kwargs):
        # No background worker/cron exists in this stack (Render free plan
        # — see CLAUDE.md), so the 60-day resolved-lead retention window is
        # enforced opportunistically here, the one page admins actually
        # visit to review resolved leads. See leads.services.purge_resolved_leads.
        purge_resolved_leads()

        context = super().get_context_data(**kwargs)
        context['survey_requests'] = SurveyRequest.objects.filter(resolved=False)
        context['contact_messages'] = ContactMessage.objects.filter(resolved=False)
        context['consultation_requests'] = ConsultationRequest.objects.filter(resolved=False)

        # Resolved leads move here — out of the per-type tables above and
        # out of every Dashboard count — combined into one list (mirroring
        # the dashboard's own cross-type Recent Activity pattern) since each
        # lead type has different fields and there's a single "Resolved
        # Requests" table, not three parallel ones.
        # Days left before purge_resolved_leads() auto-deletes each row —
        # same 60-day window, computed here rather than as a template filter
        # since it needs `now` fixed once for the whole list, not re-evaluated
        # per row on every render.
        now = timezone.now()

        def days_remaining(resolved_at):
            elapsed = (now - resolved_at).days
            return max(0, RESOLVED_LEAD_RETENTION_DAYS - elapsed)

        resolved = []
        for obj in SurveyRequest.objects.filter(resolved=True):
            resolved.append({
                'type': 'Survey Request', 'pk': obj.pk, 'name': obj.name,
                'email': obj.email, 'address': obj.address, 'problem': obj.problem,
                'why': obj.why_survey, 'received': obj.created_at, 'resolved_at': obj.resolved_at,
                'days_remaining': days_remaining(obj.resolved_at),
            })
        for obj in ContactMessage.objects.filter(resolved=True):
            resolved.append({
                'type': 'Contact Message', 'pk': obj.pk, 'name': obj.name,
                'phone': obj.phone, 'email': obj.email, 'service': obj.get_service_display(),
                'message': obj.message, 'received': obj.created_at, 'resolved_at': obj.resolved_at,
                'days_remaining': days_remaining(obj.resolved_at),
            })
        for obj in ConsultationRequest.objects.filter(resolved=True):
            resolved.append({
                'type': 'Consultation Request', 'pk': obj.pk, 'name': obj.name,
                'phone': obj.phone, 'received': obj.created_at, 'resolved_at': obj.resolved_at,
                'days_remaining': days_remaining(obj.resolved_at),
            })
        resolved.sort(key=lambda r: r['resolved_at'], reverse=True)
        context['resolved_requests'] = resolved
        return context


LEAD_TYPE_MODELS = {
    'survey': SurveyRequest,
    'contact': ContactMessage,
    'consultation': ConsultationRequest,
}


class AdminHubResolveLeadView(StaffRequiredMixin, View):
    """POST-only action from the Leads page's detail modal: marks one lead
    resolved. Called via fetch, not a real form submission — the page's own
    JS removes the row from whichever table it was in and closes the modal
    on a 200, so the admin never leaves (or reloads) the tab they were
    working through. A plain Django View (like adminhub-logout), not DRF —
    this is a same-origin AJAX POST from a server-rendered page, not a JSON
    API consumed by a React island, so a real {% csrf_token %} form (its
    hidden input read directly by the fetch call) is the simplest fit."""

    def post(self, request, lead_type, pk):
        model = LEAD_TYPE_MODELS.get(lead_type)
        if model is None:
            raise Http404
        lead = get_object_or_404(model, pk=pk)
        lead.resolved = True
        lead.resolved_at = timezone.now()
        lead.save(update_fields=['resolved', 'resolved_at'])
        return JsonResponse({'resolved': True})


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
class AdminHubProcessView(StaffRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Process Phase Photos
    # management React island, which POSTs/PATCHes/DELETEs with an
    # X-CSRFToken header.
    template_name = 'adminhub/process.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubCertificationsView(StaffRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Certifications
    # management React island, which POSTs/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/certifications.html'


@method_decorator(ensure_csrf_cookie, name='dispatch')
class AdminHubBlogView(StaffRequiredMixin, TemplateView):
    # ensure_csrf_cookie needed — this page hosts the Blog management React
    # island, which POSTs/PATCHes/DELETEs with an X-CSRFToken header.
    template_name = 'adminhub/blog.html'
