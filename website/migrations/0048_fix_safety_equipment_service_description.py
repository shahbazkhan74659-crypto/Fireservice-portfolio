from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) gave this Service row a
# description no longer matching the updated copy on
# templates/service-safety-equipment.html's hero. 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0039/0040/0041/0045/0047.
SERVICE_NAME = 'Safety Equipment'
OLD_DESCRIPTION = (
    'PPE, SCBA sets, signage and other life-safety equipment for staff and '
    'emergency responders.'
)
NEW_DESCRIPTION = (
    'We supply and support a wide range of fire and personal safety '
    'equipment to help organizations maintain a safe working environment.'
)


def fix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=NEW_DESCRIPTION)


def unfix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0047_fix_hvws_mvws_service_description'),
    ]

    operations = [
        migrations.RunPython(fix_description, unfix_description),
    ]
