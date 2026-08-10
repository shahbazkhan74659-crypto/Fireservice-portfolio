from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) gave this Service row a
# terse, feature-list-style description. 0008 is already applied against real
# dev/prod databases, so editing its RunPython body wouldn't retroactively fix
# the existing row; this migration corrects it going forward, matching the
# updated copy on templates/service-fire-detection-system.html's hero.
SERVICE_NAME = 'Fire Detection System'
OLD_DESCRIPTION = (
    'Early-warning smoke, heat and flame detection networks tied to '
    'centralized fire alarm monitoring.'
)
NEW_DESCRIPTION = (
    'We provide complete fire alarm solutions designed to detect fire at '
    'an early stage and initiate timely evacuation and emergency response.'
)


def fix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=NEW_DESCRIPTION)


def unfix_description(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=SERVICE_NAME).update(description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0038_seed_service_photos'),
    ]

    operations = [
        migrations.RunPython(fix_description, unfix_description),
    ]
