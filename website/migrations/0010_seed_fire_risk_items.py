from django.db import migrations

# One-time seed: these 12 checklist items previously lived as hardcoded <li>
# elements directly in services.html's Fire Risk Assessment section.
ITEMS = [
    'Fire hazard identification',
    'Fire risk assessment',
    'Firefighting system',
    'Fire detection and alarm system',
    'Sprinkler system',
    'Internal and external fire hydrant system',
    'Gas suppression system',
    'Fire pump house',
    'Fixed fire suppression system',
    'Fire extinguisher',
    'Passive fire protection',
    'Emergency management and life safety system',
]


def seed_items(apps, schema_editor):
    FireRiskAssessmentItem = apps.get_model('website', 'FireRiskAssessmentItem')
    for order, text in enumerate(ITEMS, start=1):
        FireRiskAssessmentItem.objects.create(text=text, order=order)


def unseed_items(apps, schema_editor):
    FireRiskAssessmentItem = apps.get_model('website', 'FireRiskAssessmentItem')
    FireRiskAssessmentItem.objects.filter(text__in=ITEMS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_fireriskassessmentitem'),
    ]

    operations = [
        migrations.RunPython(seed_items, unseed_items),
    ]
