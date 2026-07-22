from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 25 logos previously lived as hardcoded <img> tags
# pointing at static/image/client-*.png. This migration copies each source
# file into a real ClientLogo row (image field backed by MEDIA_ROOT) so the
# Admin Hub can add/edit/delete them without touching template code.
LOGOS = [
    ('client-ongc.png', 'ONGC'),
    ('client-cisf.png', 'CISF'),
    ('client-shell.png', 'Shell'),
    ('client-jll.png', 'JLL'),
    ('client-raymond.png', 'Raymond'),
    ('client-cinepolis.png', 'Cinepolis'),
    ('client-goodwill-developers.png', 'Goodwill Developers'),
    ('client-hdfc-bank.png', 'HDFC Bank'),
    ('client-crown-worldwide.png', 'Crown Worldwide Group'),
    ('client-devkrupa-enterprises.png', 'Devkrupa Enterprises'),
    ('client-petronas.png', 'Petronas'),
    ('client-neptune.png', 'Neptune'),
    ('client-basf.png', 'BASF'),
    ('client-paytm.png', 'Paytm'),
    ('client-inorbit.png', 'Inorbit'),
    ('client-aon.png', 'Aon'),
    ('client-ball.png', 'Ball Corporation'),
    ('client-oetiker.png', 'Oetiker'),
    ('client-pnb.png', 'Punjab National Bank'),
    ('client-pidilite.png', 'Pidilite'),
    ('client-bharat-gas.png', 'Bharat Gas'),
    ('client-bharat-petroleum.png', 'Bharat Petroleum'),
    ('client-kesar-group.png', 'Kesar Group'),
    ('client-g-square.png', 'G Square'),
    ('client-scottish-chemical-industries.png', 'Scottish Chemical Industries'),
]


def seed_client_logos(apps, schema_editor):
    ClientLogo = apps.get_model('website', 'ClientLogo')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'image'

    for order, (filename, name) in enumerate(LOGOS, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = ClientLogo(name=name, order=order)
        with open(src, 'rb') as f:
            obj.image.save(filename, File(f), save=True)


def unseed_client_logos(apps, schema_editor):
    ClientLogo = apps.get_model('website', 'ClientLogo')
    ClientLogo.objects.filter(name__in=[name for _, name in LOGOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_clientlogo'),
    ]

    operations = [
        migrations.RunPython(seed_client_logos, unseed_client_logos),
    ]
