from django.db import migrations

# Data-fix: renames the seed migration's (0008_seed_services.py) 'Fire
# Detection System' Service row to 'Fire Alarm System', matching the renamed
# public page (core/urls.py: service-fire-alarm-system,
# templates/service-fire-alarm-system.html). 0008 is already applied against
# real dev/prod databases, so editing its RunPython body wouldn't
# retroactively fix the existing row; this migration corrects it going
# forward, same pattern as 0035/0039/0040/0041. The icon filename
# (service-icon-fire-detection.svg / service-fire-detection-system-bg.png) is
# left untouched — it's not user-facing.
OLD_NAME = 'Fire Detection System'
NEW_NAME = 'Fire Alarm System'


def rename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=OLD_NAME).update(name=NEW_NAME)


def unrename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NEW_NAME).update(name=OLD_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0041_fix_cctv_pa_system_service_description'),
    ]

    operations = [
        migrations.RunPython(rename, unrename),
    ]
