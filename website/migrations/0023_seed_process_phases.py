from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.db import migrations

# One-time seed: these 7 phase photos previously lived as hardcoded <img>
# tags pointing at static/image/process-phase*.jpg directly in process.html.
# This migration copies each source file into a real ProcessPhase row (image
# field backed by MEDIA_ROOT) so the Admin Hub can add/edit/delete them
# without touching template code. Sourced from static/SeedImages/ (not
# static/image/) since these were never used by any other template — see
# CLAUDE.md for why that folder, not static/image/, is where seed sources
# for DB-backed content live.
PHASES = [
    ('process-phase1-site-survey.jpg', 'Field engineer conducting an on-site fire safety survey'),
    ('process-phase2-engineering-design.jpg', 'Engineers reviewing CAD/BIM fire system design drawings'),
    ('process-phase3-documentation-submission.jpg', 'Fire safety shop drawings and permit documentation compiled for submission'),
    ('process-phase4-procurement-testing.jpg', 'Fire pump testing and equipment staged at the warehouse ahead of installation'),
    ('process-phase5-installation.jpg', 'Fire mains, sprinkler risers and fire alarm control panels installed on-site'),
    ('process-phase6-testing.jpg', 'Live fire pump and sprinkler system test being witnessed by officials'),
    ('process-phase7-handover-amc.jpg', 'Client handover, staff training and ongoing AMC maintenance checks'),
]


def seed_process_phases(apps, schema_editor):
    ProcessPhase = apps.get_model('website', 'ProcessPhase')
    source_dir = Path(settings.BASE_DIR) / 'static' / 'SeedImages'

    for order, (filename, name) in enumerate(PHASES, start=1):
        src = source_dir / filename
        if not src.exists():
            continue
        obj = ProcessPhase(name=name, order=order)
        with open(src, 'rb') as f:
            obj.image.save(filename, File(f), save=True)


def unseed_process_phases(apps, schema_editor):
    ProcessPhase = apps.get_model('website', 'ProcessPhase')
    ProcessPhase.objects.filter(name__in=[name for _, name in PHASES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0022_processphase'),
    ]

    operations = [
        migrations.RunPython(seed_process_phases, unseed_process_phases),
    ]
