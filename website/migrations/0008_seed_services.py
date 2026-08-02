from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 8 service cards previously lived as hardcoded <div
# class="card"> blocks (with inline SVG icons) directly in services.html.
# This migration copies each icon into a real Service row (icon field
# backed by MEDIA_ROOT) so the Admin Hub can add/edit/delete them without
# touching template code. The icon source files are standalone SVGs
# extracted from the original inline <svg> markup, with the stroke color
# baked in as white (matching the original .card__icon CSS) since an
# <img src="..."> can't be styled by the page's external CSS the way an
# inline <svg> could.
SERVICES = [
    (
        'service-icon-fire-detection.svg',
        'Fire Detection System',
        'Early-warning smoke, heat and flame detection networks tied to centralized fire alarm monitoring.',
    ),
    (
        'service-icon-co2-flooding.svg',
        'Co2 Gas Flooding',
        'Clean-agent CO2 flooding systems for server rooms, archives and other high-value, water-sensitive spaces.',
    ),
    (
        'service-icon-cctv-pa.svg',
        'CCTV & PA System',
        'Surveillance and zone-based public address systems for security monitoring and emergency announcements.',
    ),
    (
        'service-icon-hvws-mvms.svg',
        'HVWS / MVMS System',
        'High- and medium-velocity water spray systems for transformer, turbine and high-hazard area protection.',
    ),
    (
        'service-icon-fire-extinguisher.svg',
        'All Type Fire Extinguisher',
        'Supply, installation, refilling and certification of extinguishers for every hazard class.',
    ),
    (
        'service-icon-safety-equipment.svg',
        'Safety Equipment',
        'PPE, SCBA sets, signage and other life-safety equipment for staff and emergency responders.',
    ),
    (
        'service-icon-fire-pump-house.svg',
        'Fire Pump House',
        'Design, installation and maintenance of fire pump houses and associated hydraulic infrastructure.',
    ),
    (
        'service-icon-electricals.svg',
        'All Type Electricals Work',
        'Electrical wiring, panel work and low-voltage installations supporting fire and life-safety systems.',
    ),
]


def seed_services(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'SeedImages'

    for order, (filename, name, description) in enumerate(SERVICES, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = Service(name=name, description=description, order=order)
        with open(src, 'rb') as f:
            obj.icon.save(filename, File(f), save=True)


def unseed_services(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name__in=[name for _, name, _ in SERVICES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0007_service'),
    ]

    operations = [
        migrations.RunPython(seed_services, unseed_services),
    ]
