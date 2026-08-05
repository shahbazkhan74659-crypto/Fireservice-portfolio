from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0004_consultationrequest_resolved_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactmessage',
            name='service',
            field=models.CharField(
                choices=[
                    ('fire_detection', 'Fire Detection System'),
                    ('co2_gas_flooding', 'Co2 Gas Flooding'),
                    ('cctv_pa', 'CCTV & PA System'),
                    ('hvws_mvms', 'HVWS / MVWS System'),
                    ('fire_extinguisher', 'All Type Fire Extinguisher'),
                    ('safety_equipment', 'Safety Equipment'),
                    ('fire_pump_house', 'Fire Pump House'),
                    ('electricals', 'All Type Electricals Work'),
                    ('other', 'Not sure / Other'),
                ],
                default='other',
                max_length=30,
            ),
        ),
    ]
