from django.db import migrations

# Data-fix: reorders the seeded Service rows (website/migrations/0008_seed_
# services.py) so 'Fire Pump House' moves from position 7 to position 4,
# shifting 'HVWS / MVWS System', 'All Type Fire Extinguisher' and 'Safety
# Equipment' down by one each. This 'order' field drives both the display
# sequence on /services/ (Service's default ordering = ['order', 'id']) and
# each card's "Phase N" ribbon. 0008 is already applied against real dev/prod
# databases, so editing its RunPython body wouldn't retroactively reorder the
# existing rows; this migration corrects it going forward, same pattern as
# 0035/0039-0041/0045.
NEW_ORDER = {
    'Fire Pump House': 4,
    'HVWS / MVWS System': 5,
    'All Type Fire Extinguisher': 6,
    'Safety Equipment': 7,
}
OLD_ORDER = {
    'Fire Pump House': 7,
    'HVWS / MVWS System': 4,
    'All Type Fire Extinguisher': 5,
    'Safety Equipment': 6,
}


def reorder(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    for name, order in NEW_ORDER.items():
        Service.objects.filter(name=name).update(order=order)


def unreorder(apps, schema_editor):
    Service = apps.get_model('website', 'Service')
    for name, order in OLD_ORDER.items():
        Service.objects.filter(name=name).update(order=order)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0045_fix_fire_pump_house_service_description'),
    ]

    operations = [
        migrations.RunPython(reorder, unreorder),
    ]
