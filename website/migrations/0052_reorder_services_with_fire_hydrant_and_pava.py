from django.db import migrations

# Data-fix: finishes reordering the 9 Service rows now that 'Fire Hydrant
# System' (order=5, seeded by 0051) and 'PAVA System' (renamed from 'All Type
# Electricals Work' by 0050) both exist. Final order requested by the client,
# matching the sequence their own content list used:
#   1 Fire Alarm System        (unchanged)
#   2 Gas Detection System     (unchanged)
#   3 Gas Suppression System   (unchanged)
#   4 Fire Pump House          (unchanged, see 0046)
#   5 Fire Hydrant System      (already set by 0051)
#   6 PAVA System              (was 8)
#   7 HVWS / MVWS System       (was 5)
#   8 Safety Equipment         (was 7)
#   9 Fire Extinguishers       (was 6)
# This 'order' field drives both the /services/ display sequence (Service's
# default ordering = ['order', 'id']) and each card's "Phase N" ribbon.
NEW_ORDER = {
    'PAVA System': 6,
    'HVWS / MVWS System': 7,
    'Safety Equipment': 8,
    'Fire Extinguishers': 9,
}
OLD_ORDER = {
    'PAVA System': 8,
    'HVWS / MVWS System': 5,
    'Safety Equipment': 7,
    'Fire Extinguishers': 6,
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
        ('website', '0051_seed_fire_hydrant_system_service'),
    ]

    operations = [
        migrations.RunPython(reorder, unreorder),
    ]
