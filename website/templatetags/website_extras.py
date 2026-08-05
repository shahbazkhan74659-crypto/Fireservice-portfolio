import json

from django import template

from core.context_processors import BUSINESS_NAME
from website.models import Brand, Certification, ClientLogo, HeroSlide, Product, ProcessPhase, Service, SiteSetting

register = template.Library()


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
