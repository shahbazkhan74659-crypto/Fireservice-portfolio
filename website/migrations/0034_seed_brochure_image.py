from django.db import migrations


def render_brochure_image(apps, schema_editor):
    # Historical model state doesn't have the real render_pdf_first_page_to_png()
    # helper available in the same form, so this imports the actual current
    # module (safe here — the function's behavior isn't part of the schema
    # being migrated, only used to populate data).
    from website.pdf_utils import render_pdf_first_page_to_png

    Brochure = apps.get_model('website', 'Brochure')
    brochure = Brochure.objects.filter(pk=1).first()
    if not brochure or not brochure.pdf:
        return

    brochure.pdf.open('rb')
    try:
        image_file = render_pdf_first_page_to_png(brochure.pdf, 'its-brochure')
    finally:
        brochure.pdf.close()
    brochure.image.save(image_file.name, image_file, save=True)


def unrender_brochure_image(apps, schema_editor):
    Brochure = apps.get_model('website', 'Brochure')
    brochure = Brochure.objects.filter(pk=1).first()
    if brochure and brochure.image:
        brochure.image.delete(save=True)


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0033_brochure_image'),
    ]

    operations = [
        migrations.RunPython(render_brochure_image, unrender_brochure_image),
    ]
