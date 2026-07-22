from django.db import migrations

MISSION = {
    'title': 'Our Mission',
    'body': (
        'We commit to preventing and suppressing destructive fires, investigating their causes, '
        'and enforcing fire codes and other related regulations. We respond to man-made and '
        'natural disasters and other emergencies — conducting business to the highest standards '
        'of ethics, honesty and integrity in every engagement.'
    ),
    'points': [
        'Prevent & suppress destructive fires',
        'Investigate root causes',
        'Enforce fire codes & related regulations',
        'Respond to emergencies — man-made and natural',
    ],
    'order': 1,
}

VISION = {
    'title': 'Our Vision',
    'body': (
        'To grow as a technology-driven engineering organization dedicated to excellence through '
        'quality — creating value for customers and employees alike through innovation, '
        'technology and operational expertise. Customer satisfaction and shareholder value are our '
        'primary measures of success, pursued with an unwavering commitment to quality and an '
        'open, transparent way of dealing with our customers.'
    ),
    'points': [
        'Innovation & operational expertise',
        'Customer satisfaction & shareholder value',
        'Continual improvement of people, process & product',
        'Open, transparent, ethical dealing',
    ],
    'order': 2,
}


def seed_items(apps, schema_editor):
    MissionVisionItem = apps.get_model('website', 'MissionVisionItem')
    MissionVisionItem.objects.create(**MISSION)
    MissionVisionItem.objects.create(**VISION)


def unseed_items(apps, schema_editor):
    MissionVisionItem = apps.get_model('website', 'MissionVisionItem')
    MissionVisionItem.objects.filter(title__in=['Our Mission', 'Our Vision']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_items, unseed_items),
    ]
