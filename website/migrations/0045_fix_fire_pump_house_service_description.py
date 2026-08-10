from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) gave this Service row a
# description no longer matching the updated copy on
# templates/service-fire-pump-house.html's hero. 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0039/0040/0041.
SERVICE_NAME = 'Fire Pump House'
OLD_DESCRIPTION = (
    'Design, installation and maintenance of fire pump houses and '
    'associated hydraulic infrastructure.'
)
NEW_DESCRIPTION = (
    'We provide engineering and project support for complete fire pump '
    'house systems to ensure dependable water supply for firefighting '
    'applications.'
)


def fix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=NEW_DESCRIPTION)


def unfix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0044_rename_cctv_pa_to_gas_suppression_system'),
    ]

    operations = [
        migrations.RunPython(fix_description, unfix_description),
    ]
