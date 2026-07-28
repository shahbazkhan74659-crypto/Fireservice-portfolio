from django.contrib.sitemaps import Sitemap
from django.urls import reverse

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
