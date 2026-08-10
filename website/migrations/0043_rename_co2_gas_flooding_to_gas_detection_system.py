from django.db import migrations

# Data-fix: renames the seed migration's (0008_seed_services.py) 'Co2 Gas
# Flooding' Service row to 'Gas Detection System', matching the renamed
# public page (core/urls.py: service-gas-detection-system,
# templates/service-gas-detection-system.html). 0008 is already applied
# against real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0035/0039/0040/0041/0042. The icon filename
# (service-icon-co2-flooding.svg / service-co2-gas-flooding-bg.png) is left
# untouched — it's not user-facing.
OLD_NAME = 'Co2 Gas Flooding'
NEW_NAME = 'Gas Detection System'


def rename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=OLD_NAME).update(name=NEW_NAME)


def unrename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NEW_NAME).update(name=OLD_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0042_rename_fire_detection_to_fire_alarm_system'),
    ]

    operations = [
        migrations.RunPython(rename, unrename),
    ]
