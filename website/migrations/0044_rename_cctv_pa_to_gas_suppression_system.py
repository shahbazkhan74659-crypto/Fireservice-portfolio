from django.db import migrations

# Data-fix: renames the seed migration's (0008_seed_services.py) 'CCTV & PA
# System' Service row to 'Gas Suppression System', matching the renamed
# public page (core/urls.py: service-gas-suppression-system,
# templates/service-gas-suppression-system.html). 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0035/0039/0040/0041/0042/0043. The icon filename
# (service-icon-cctv-pa.svg / service-cctv-pa-system-bg.png) is left
# untouched — it's not user-facing.
OLD_NAME = 'CCTV & PA System'
NEW_NAME = 'Gas Suppression System'


def rename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=OLD_NAME).update(name=NEW_NAME)


def unrename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NEW_NAME).update(name=OLD_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0043_rename_co2_gas_flooding_to_gas_detection_system'),
    ]

    operations = [
        migrations.RunPython(rename, unrename),
    ]
