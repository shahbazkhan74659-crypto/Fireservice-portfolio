from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) gave this Service row a
# description no longer matching the updated copy on
# templates/service-cctv-pa-system.html's hero. 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0039/0040.
SERVICE_NAME = 'CCTV & PA System'
OLD_DESCRIPTION = (
    'Surveillance and zone-based public address systems for security '
    'monitoring and emergency announcements.'
)
NEW_DESCRIPTION = (
    'We design and engineer automatic fire suppression systems for areas '
    'where water-based firefighting may not be suitable, particularly for '
    'critical equipment and sensitive environments.'
)


def fix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=NEW_DESCRIPTION)


def unfix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0040_fix_co2_gas_flooding_service_description'),
    ]

    operations = [
        migrations.RunPython(fix_description, unfix_description),
    ]
