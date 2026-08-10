from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) gave this Service row a
# description no longer matching the updated copy on
# templates/service-hvws-mvws-system.html's hero. 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0039/0040/0041/0045.
SERVICE_NAME = 'HVWS / MVWS System'
OLD_DESCRIPTION = (
    'High- and medium-velocity water spray systems for transformer, '
    'turbine and high-hazard area protection.'
)
NEW_DESCRIPTION = (
    'We provide engineering solutions for High Velocity Water Spray (HVWS) '
    'and Medium Velocity Water Spray (MVWS) fire protection systems for '
    'high-risk equipment and process areas.'
)


def fix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=NEW_DESCRIPTION)


def unfix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0046_move_fire_pump_house_to_phase_4'),
    ]

    operations = [
        migrations.RunPython(fix_description, unfix_description),
    ]
