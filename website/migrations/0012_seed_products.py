from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 18 product photos previously lived as hardcoded <img>
# tags pointing at static/image/product-*.jpg. This migration copies each
# source file into a real Product row (image field backed by MEDIA_ROOT) so
# the Admin Hub can add/edit/delete them without touching template code.
PRODUCTS = [
    ('product-fire-alarm-system.jpg', 'Fire Alarm System'),
    ('product-manual-call-point.jpg', 'Manual Call Point'),
    ('product-fire-signage.jpg', 'Fire Signage'),
    ('product-fire-sprinklers.jpg', 'Fire Sprinklers'),
    ('product-scba-set.jpg', 'SCBA Sets'),
    ('product-ppe.jpg', 'PPE Products'),
    ('product-fire-extinguishers.jpg', 'All Types of Fire Extinguishers'),
    ('product-smoke-alarm.jpg', 'Smoke Alarms'),
    ('product-fire-hydrants.jpg', 'Fire Hydrants'),
    ('product-hose-box.jpg', 'Hose Box'),
    ('product-fire-blankets.jpg', 'Fire Blankets'),
    ('product-valves.jpg', 'All Types of Valves'),
    ('product-hose-reel-drum.jpg', 'Hose Reel Drum'),
    ('product-nozzles.jpg', 'All Types of Nozzles'),
    ('product-fire-ball.jpg', 'Fire Ball'),
    ('product-water-foam-monitor.jpg', 'Water Foam Monitor'),
    ('product-fire-extinguisher-stand.jpg', 'Fire Extinguisher Stand'),
    ('product-spill-kit.jpg', 'Spill Kit'),
]


def seed_products(apps, schema_editor):
    Product = apps.get_model('website', 'Product')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'image'

    for order, (filename, name) in enumerate(PRODUCTS, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = Product(name=name, order=order)
        with open(src, 'rb') as f:
            obj.image.save(filename, File(f), save=True)


def unseed_products(apps, schema_editor):
    Product = apps.get_model('website', 'Product')
    Product.objects.filter(name__in=[name for _, name in PRODUCTS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0011_product'),
    ]

    operations = [
        migrations.RunPython(seed_products, unseed_products),
    ]
