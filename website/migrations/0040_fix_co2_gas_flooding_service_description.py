from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) gave this Service row a
# description no longer matching the updated copy on
# templates/service-co2-gas-flooding.html's hero. 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0039_fix_fire_detection_service_description.py.
SERVICE_NAME = 'Co2 Gas Flooding'
OLD_DESCRIPTION = (
    'Clean-agent CO2 flooding systems for server rooms, archives and other '
    'high-value, water-sensitive spaces.'
)
NEW_DESCRIPTION = (
    'Our gas detection solutions help identify hazardous and combustible '
    'gases and provide early warning to protect personnel, equipment, and '
    'facilities.'
)


def fix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=NEW_DESCRIPTION)


def unfix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0039_fix_fire_detection_service_description'),
    ]

    operations = [
        migrations.RunPython(fix_description, unfix_description),
    ]
