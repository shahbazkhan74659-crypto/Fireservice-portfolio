from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0008_seed_services'),
    ]

    operations = [
        migrations.CreateModel(
            name='FireRiskAssessmentItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=200)),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]
