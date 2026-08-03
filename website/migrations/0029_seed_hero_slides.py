from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 4 slideshow photos previously lived as hardcoded
# background-image rules (.hero__bg-slide--1..4) directly in style.css.
# This migration copies each source file into a real HeroSlide row (image
# field backed by MEDIA_ROOT) so the slideshow is DB-driven everywhere
# includes/hero-bg-slideshow.html is reused, without touching template/CSS
# code to add/remove/reorder a slide. Sourced from static/SeedImages/ (not
# static/image/, which they were moved out of in this same change) — see
# CLAUDE.md for why that folder, not static/image/, is where seed sources
# for DB-backed content live.
SLIDES = [
    'bg-image.jpg',
    'achievements-growth-illustration.jpg',
    'brochure-fire-safety-training.jpg',
    'about-fire-extinguishers.jpg',
]


def seed_hero_slides(apps, schema_editor):
    HeroSlide = apps.get_model('website', 'HeroSlide')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'SeedImages'

    for order, filename in enumerate(SLIDES, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = HeroSlide(order=order)
        with open(src, 'rb') as f:
            obj.image.save(filename, File(f), save=True)


def unseed_hero_slides(apps, schema_editor):
    HeroSlide = apps.get_model('website', 'HeroSlide')
    HeroSlide.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0028_heroslide'),
    ]

    operations = [
        migrations.RunPython(seed_hero_slides, unseed_hero_slides),
    ]
