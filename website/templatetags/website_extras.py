import json

from django import template
from django.urls import reverse

from core.context_processors import BUSINESS_NAME
from website.models import Brand, Certification, ClientLogo, HeroSlide, Product, ProcessPhase, Service, SiteSetting

register = template.Library()

# Maps each seeded Service row's exact `name` (see
# website/migrations/0008_seed_services.py) to its fixed public detail page
# — these are hand-authored pages (core/views.py), not a DB-driven slug, so
# the mapping lives here rather than on the model itself.
SERVICE_PAGE_URL_NAMES = {
    'Fire Alarm System': 'service-fire-alarm-system',
    'Gas Detection System': 'service-gas-detection-system',
    'Gas Suppression System': 'service-gas-suppression-system',
    'HVWS / MVWS System': 'service-hvws-mvws-system',
    'Fire Extinguishers': 'service-fire-extinguishers',
    'Safety Equipment': 'service-safety-equipment',
    'Fire Pump House': 'service-fire-pump-house',
    'Fire Hydrant System': 'service-fire-hydrant-system',
    'PAVA System': 'service-pava-system',
}


@register.filter
def service_page_url(service_name):
    """Falls back to the Services list page itself for any name without a
    dedicated page yet (e.g. a new Service added via the Admin Hub CRUD
    before its fixed page exists) — never a broken link."""
    url_name = SERVICE_PAGE_URL_NAMES.get(service_name)
    return reverse(url_name) if url_name else reverse('services')


@register.simple_tag
def get_client_logos():
    return ClientLogo.objects.all()


@register.simple_tag
def get_brands():
    return Brand.objects.all()


@register.simple_tag
def get_products():
    return Product.objects.all()


@register.simple_tag
def get_process_phases():
    return ProcessPhase.objects.all()


@register.simple_tag
def get_hero_slides():
    return HeroSlide.objects.all()


@register.simple_tag
def get_services():
    return Service.objects.all()


@register.simple_tag
def get_certifications():
    return Certification.objects.all()


@register.simple_tag(takes_context=True)
def get_certifications_jsonld(context):
    """Certification JSON-LD (@graph of schema.org/Certification nodes), built
    from real Certification rows only — name/description/meta/image, the same
    fields already looped in certifications.html's own .cert-grid, not
    fabricated copy. Built with json.dumps() rather than template-side
    {{ }} interpolation, matching the exact rationale already documented in
    core/context_processors.py's `seo()` and core/views.py's ServicesView:
    Certification.description/meta are admin-editable free text that could
    contain quotes/ampersands Django's HTML auto-escaping would otherwise
    corrupt inside a JSON string. No issuedBy/expires/datePublished fields —
    no structured source data exists for them in the model, and fabricating
    them from the free-text `meta` field would be wrong."""
    request = context['request']
    origin = 'https' if request.is_secure() else 'http'
    origin = f'{origin}://{request.get_host()}'

    return json.dumps({
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'Certification',
                'name': certification.name,
                'description': certification.description,
                'certificationIdentification': certification.meta,
                'image': f'{origin}{certification.image.url}',
                'about': {
                    '@type': 'LocalBusiness',
                    'name': BUSINESS_NAME,
                },
            }
            for certification in Certification.objects.all()
        ],
    })


@register.simple_tag
def get_years_experience():
    return SiteSetting.load().years_experience


@register.simple_tag
def get_clients_served():
    return SiteSetting.load().clients_served


@register.simple_tag
def get_installations():
    return SiteSetting.load().installations


@register.simple_tag
def get_emergency_support():
    return SiteSetting.load().emergency_support


@register.simple_tag
def get_team_members():
    return SiteSetting.load().team_members


@register.simple_tag
def get_hero_slide_duration():
    return SiteSetting.load().hero_slide_duration_seconds
