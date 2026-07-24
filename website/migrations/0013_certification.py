from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0012_seed_products'),
    ]

    operations = [
        migrations.CreateModel(
            name='Certification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('description', models.CharField(max_length=200)),
                ('meta', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='certifications/')),
                ('order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
    ]
