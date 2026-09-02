from django.db import migrations

# One-time seed of obviously-fake placeholder rows so the Admin Hub and the
# public Home page section have something to show the layout before the
# client adds real customer testimonials — see CLAUDE.md's "Content still
# needed from client" (no real testimonial quotes exist yet). Each row is
# deliberately named/worded so nobody mistakes it for a real quote.
TESTIMONIALS = [
    {
        'name': 'Sample Customer',
        'company': 'Sample Company Pvt. Ltd.',
        'quote': (
            'This is a placeholder testimonial. Replace it with a real customer '
            'quote from the Admin Hub before this goes live.'
        ),
        'rating': 5,
        'order': 1,
    },
    {
        'name': 'Sample Customer 2',
        'company': 'Sample Company 2 Pvt. Ltd.',
        'quote': (
            'Add your real customers’ feedback here via Admin Hub → Clientele → '
            'Testimonials. This placeholder will keep showing until it’s replaced.'
        ),
        'rating': 5,
        'order': 2,
    },
    {
        'name': 'Sample Customer 3',
        'company': 'Sample Company 3 Pvt. Ltd.',
        'quote': 'Placeholder testimonial — edit or delete this once real customer reviews are available.',
        'rating': 4,
        'order': 3,
    },
]


def seed_testimonials(apps, schema_editor):
    Testimonial = apps.get_model('website', 'Testimonial')
    for data in TESTIMONIALS:
        Testimonial.objects.create(**data)


def unseed_testimonials(apps, schema_editor):
    Testimonial = apps.get_model('website', 'Testimonial')
    Testimonial.objects.filter(name__in=[t['name'] for t in TESTIMONIALS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0057_testimonial'),
    ]

    operations = [
        migrations.RunPython(seed_testimonials, unseed_testimonials),
    ]
