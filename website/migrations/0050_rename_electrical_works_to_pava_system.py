from django.db import migrations

# Data-fix: renames the seed migration's (0008_seed_services.py) 'All Type
# Electricals Work' Service row to 'PAVA System', matching the renamed
# public page (core/urls.py: service-pava-system,
# templates/service-pava-system.html). This isn't a like-for-like content
# swap — Electricals Work's old body copy (wiring/panel work) has nothing to
# do with a Public Address and Voice Alarm system, so the template's body
# copy was rewritten from scratch, unlike the description-only fixes
# elsewhere in this migration sequence. 0008 is already applied against real
# dev/prod databases, so editing its RunPython body wouldn't retroactively
# fix the existing row; this migration corrects it going forward, same
# pattern as 0035/0039-0041/0044/0045/0047-0049. The icon filename
# (service-icon-electrical.svg / service-electrical-works-bg.png) is left
# untouched — it's not user-facing.
OLD_NAME = 'All Type Electricals Work'
NEW_NAME = 'PAVA System'
OLD_DESCRIPTION = (
    'Electrical wiring, panel work and low-voltage installations '
    'supporting fire and life-safety systems.'
)
NEW_DESCRIPTION = (
    'We provide Public Address and Voice Alarm (PAVA) systems for '
    'emergency communication, evacuation, and public announcements.'
)


def rename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=OLD_NAME).update(name=NEW_NAME, description=NEW_DESCRIPTION)


def unrename(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    Service.objects.filter(name=NEW_NAME).update(name=OLD_NAME, description=OLD_DESCRIPTION)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0049_rename_fire_extinguisher_service'),
    ]

    operations = [
        migrations.RunPython(rename, unrename),
    ]
