import json

from django.templatetags.static import static

# Short, plain-text (no HTML entities) breadcrumb labels for every real
# public page's url name (see core/urls.py) — kept separate from each
# page's <title> text on purpose, since <title>/og:title strings contain
# literal HTML entities (e.g. "&amp;") that would render wrong if dropped
# straight into a JSON-LD string (JSON has no concept of HTML entities).
BREADCRUMB_NAMES = {
    'about': 'About Us',
    'services': 'Services',
    'process': 'Our Process',
    'clientele': 'Clientele',
    'certifications': 'Certifications',
    'contact': 'Contact Us',
    'survey': 'Free Site Survey',
    'consultation': 'Free Consultation',
    'brochure': 'Brochure',
    'blog': 'Blog',
}

# Real NAP data already used elsewhere in the project (topbar/footer via
# includes/address.html + includes/phone.html + includes/email.html, and
# the Instagram link via includes/instagram.html) — reused here rather than
# re-derived, so the LocalBusiness JSON-LD can never drift out of sync with
# what's already shown on the page. No aggregateRating/openingHours/review
# fields are included since none of that is real, confirmed data anywhere
# in this project — fabricating them would be a Google manual-action risk,
# not a neutral placeholder.
BUSINESS_NAME = 'Iconic Techno Service'
BUSINESS_PHONES = ['+91 73592 29129']
BUSINESS_EMAIL = 'iconictechnoservice.in@gmail.com'
BUSINESS_ADDRESS = {
    '@type': 'PostalAddress',
    'streetAddress': 'Shop No. 17, First Floor, Indraprasth Arcade, Tokarkhada',
    'addressLocality': 'Silvassa',
    'postalCode': '396230',
    'addressRegion': 'Dadra and Nagar Haveli and Daman and Diu',
    'addressCountry': 'IN',
}
BUSINESS_INSTAGRAM = 'https://www.instagram.com/iconictechnoservice.in__2929'


def seo(request):
    """Sitewide SEO context available on every template (registered in
    TEMPLATES/OPTIONS/context_processors alongside the existing `request`
    processor) — canonical URL, the default (logo) og:image, and two
    pre-serialized JSON-LD blocks (LocalBusiness + BreadcrumbList).

    JSON-LD is built with json.dumps() here rather than assembled in the
    template with Django's `{{ var }}` auto-escaping, specifically to avoid
    a real correctness bug: auto-escaping converts quotes/ampersands into
    HTML entities, which is correct for HTML but corrupts a JSON string
    (Google would still parse it — the entities aren't a syntax error — but
    the rich-result text would visibly show "&amp;" instead of "&"). This
    matters most for the Services page's Service JSON-LD, which is built
    from admin-editable free-text `Service.description` values that could
    contain quotes/ampersands in the future.
    """
    origin = 'https' if request.is_secure() else 'http'
    origin = f'{origin}://{request.get_host()}'
    canonical_url = f'{origin}{request.path}'
    logo_url = f"{origin}{static('image/logo-its-dark.png')}"

    local_business_jsonld = json.dumps({
        '@context': 'https://schema.org',
        '@type': 'LocalBusiness',
        'name': BUSINESS_NAME,
        'image': logo_url,
        'logo': logo_url,
        'url': f'{origin}/',
        'telephone': BUSINESS_PHONES,
        'email': BUSINESS_EMAIL,
        'address': BUSINESS_ADDRESS,
        'sameAs': [BUSINESS_INSTAGRAM],
    })

    breadcrumb_jsonld = None
    url_name = getattr(request.resolver_match, 'url_name', None)
    page_name = BREADCRUMB_NAMES.get(url_name)
    if page_name:
        breadcrumb_jsonld = json.dumps({
            '@context': 'https://schema.org',
            '@type': 'BreadcrumbList',
            'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': f'{origin}/'},
                {'@type': 'ListItem', 'position': 2, 'name': page_name, 'item': canonical_url},
            ],
        })

    return {
        'site_origin': origin,
        'canonical_url': canonical_url,
        'og_image_default': logo_url,
        'local_business_jsonld': local_business_jsonld,
        'breadcrumb_jsonld': breadcrumb_jsonld,
    }
