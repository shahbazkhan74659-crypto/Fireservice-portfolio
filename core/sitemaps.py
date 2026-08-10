from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from core.locations import LOCATIONS
from website.models import BlogPost

# Every real public page's url name (see core/urls.py) — deliberately
# excludes Admin Hub (/admin-hub/*) and the API-only /api/* surface, neither
# of which should ever be indexed. The home page gets a higher priority/more
# frequent changefreq than the rest since it's the most likely entry point
# and updates most often (hero stats, recent client-logo strip).
PUBLIC_PAGES = {
    'home': {'changefreq': 'weekly', 'priority': 1.0},
    'about': {'changefreq': 'monthly', 'priority': 0.7},
    'services': {'changefreq': 'monthly', 'priority': 0.9},
    'process': {'changefreq': 'monthly', 'priority': 0.6},
    'clientele': {'changefreq': 'monthly', 'priority': 0.6},
    'certifications': {'changefreq': 'monthly', 'priority': 0.6},
    'contact': {'changefreq': 'yearly', 'priority': 0.8},
    'survey': {'changefreq': 'yearly', 'priority': 0.8},
    'consultation': {'changefreq': 'yearly', 'priority': 0.8},
    'brochure': {'changefreq': 'yearly', 'priority': 0.5},
    'blog': {'changefreq': 'weekly', 'priority': 0.7},
    'service-fire-alarm-system': {'changefreq': 'monthly', 'priority': 0.6},
    'service-gas-detection-system': {'changefreq': 'monthly', 'priority': 0.6},
    'service-gas-suppression-system': {'changefreq': 'monthly', 'priority': 0.6},
    'service-hvws-mvws-system': {'changefreq': 'monthly', 'priority': 0.6},
    'service-fire-extinguishers': {'changefreq': 'monthly', 'priority': 0.6},
    'service-safety-equipment': {'changefreq': 'monthly', 'priority': 0.6},
    'service-fire-pump-house': {'changefreq': 'monthly', 'priority': 0.6},
    'service-fire-hydrant-system': {'changefreq': 'monthly', 'priority': 0.6},
    'service-pava-system': {'changefreq': 'monthly', 'priority': 0.6},
}


class StaticViewSitemap(Sitemap):
    def items(self):
        return list(PUBLIC_PAGES.keys())

    def location(self, item):
        return reverse(item)

    def changefreq(self, item):
        return PUBLIC_PAGES[item]['changefreq']

    def priority(self, item):
        return PUBLIC_PAGES[item]['priority']


class BlogPostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog-detail', args=[obj.slug])


class LocationSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return LOCATIONS

    def location(self, item):
        return reverse('location', args=[item['slug']])
