from django.core.management import call_command
from django.db import migrations

CACHE_TABLE_NAME = 'django_cache'


def create_cache_table(apps, schema_editor):
    call_command('createcachetable', CACHE_TABLE_NAME)


def drop_cache_table(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f'DROP TABLE IF EXISTS {CACHE_TABLE_NAME}')


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.RunPython(create_cache_table, drop_cache_table),
    ]
