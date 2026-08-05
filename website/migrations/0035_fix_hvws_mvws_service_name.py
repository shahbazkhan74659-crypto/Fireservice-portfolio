from django.db import migrations

# Data-fix: the seed migration (0008_seed_services.py) named this Service row
# 'HVWS / MVMS System', but the correct industry/search term for the medium-
# velocity variant is MVWS (Medium Velocity Water Spray), not MVMS — MVMS
# isn't a real term. 0008 is already applied against real dev/prod databases,
# so editing its RunPython body wouldn't retroactively fix the existing row;
# this migration corrects it going forward. The icon filename
# (service-icon-hvws-mvms.svg) is left untouched — it's not user-facing.
OLD_NAME = 'HVWS / MVMS System'
NEW_NAME = 'HVWS / MVWS System'


def fix_name(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=OLD_NAME).update(name=NEW_NAME)


def unfix_name(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NEW_NAME).update(name=OLD_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0034_seed_brochure_image'),
    ]

    operations = [
        migrations.RunPython(fix_name, unfix_name),
    ]
