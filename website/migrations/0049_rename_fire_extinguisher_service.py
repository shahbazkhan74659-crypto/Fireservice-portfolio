from django.db import migrations

# Data-fix: renames the seed migration's (0008_seed_services.py) 'All Type
# Fire Extinguisher' Service row to 'Fire Extinguishers' and updates its
# description, matching templates/service-fire-extinguishers.html's hero.
# The URL (service-fire-extinguishers) is unchanged since it already matched.
# 0008 is already applied against real dev/prod databases, so editing its
# RunPython body wouldn't retroactively fix the existing row; this migration
# corrects it going forward, same pattern as 0035/0039-0041/0045/0047/0048.
OLD_NAME = 'All Type Fire Extinguisher'
NEW_NAME = 'Fire Extinguishers'
OLD_DESCRIPTION = (
    'Supply, installation, refilling and certification of extinguishers '
    'for every hazard class.'
)
NEW_DESCRIPTION = (
    'We provide suitable fire extinguishers for different types of fire '
    'hazards and applications.'
)


def rename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=OLD_NAME).update(name=NEW_NAME, description=NEW_DESCRIPTION)


def unrename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NEW_NAME).update(name=OLD_NAME, description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0048_fix_safety_equipment_service_description'),
    ]

    operations = [
        migrations.RunPython(rename, unrename),
    ]
