from django.db import migrations

# One-time seed: "10+ Years Experience" was previously hardcoded in every
# stats-bar template (Home/About/Consultation/Clientele). This creates the
# singleton row (pk=1) with that same value so nothing changes on the public
# site until someone edits it from the Admin Home dashboard.


def seed_site_setting(apps, schema_editor):
    SiteSetting = apps.get_model('website', 'SiteSetting')
    SiteSetting.objects.get_or_create(pk=1, defaults={'years_experience': 10})


def unseed_site_setting(apps, schema_editor):
    SiteSetting = apps.get_model('website', 'SiteSetting')
    SiteSetting.objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_sitesetting'),
    ]

    operations = [
        migrations.RunPython(seed_site_setting, unseed_site_setting),
    ]
