from django.db import migrations

# Adds a genuinely new Service row for the 9th fixed service page,
# 'Fire Hydrant System' (core/urls.py: service-fire-hydrant-system,
# templates/service-fire-hydrant-system.html) — unlike every other migration
# in this sequence, there's no existing seeded row to rename here. icon is
# left blank ('') since no photo asset exists yet for this service (same
# "content still needed from client" situation as the About page's team
# photo — see CLAUDE.md); the public page and its /services/ card both
# already degrade gracefully to no thumbnail when Service.icon is empty.
# order=5 slots it in right after Fire Pump House — see
# 0052_reorder_services_with_fire_hydrant_and_pava.py, applied next, for the
# full final ordering of all 9 services.
NAME = 'Fire Hydrant System'
DESCRIPTION = (
    'Our fire hydrant systems provide reliable firefighting water '
    'distribution throughout industrial, commercial, and infrastructure '
    'facilities.'
)
ORDER = 5


def seed(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.get_or_create(
        name=NAME,
        defaults={'description': DESCRIPTION, 'icon': '', 'order': ORDER},
    )


def unseed(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0050_rename_electrical_works_to_pava_system'),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
