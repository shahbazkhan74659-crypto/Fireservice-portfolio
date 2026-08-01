from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0020_sitesetting_verbose_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='certification',
            name='pdf',
            field=models.FileField(blank=True, null=True, upload_to='certifications/pdfs/'),
        ),
    ]
