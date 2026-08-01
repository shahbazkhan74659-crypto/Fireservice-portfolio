import pytest

from website.models import Brand, Certification, SiteSetting

pytestmark = pytest.mark.django_db


class TestSiteSettingSingleton:
    def test_load_creates_row_with_defaults(self):
        setting = SiteSetting.load()
        assert setting.pk == 1
        assert setting.years_experience == 10

    def test_load_is_idempotent_and_returns_the_same_row(self):
        first = SiteSetting.load()
        first.years_experience = 25
        first.save()

        second = SiteSetting.load()

        assert second.pk == first.pk == 1
        assert second.years_experience == 25
        assert SiteSetting.objects.count() == 1

    def test_save_always_pins_pk_to_1_even_for_a_fresh_instance(self):
        setting = SiteSetting(years_experience=5)
        setting.save()
        assert setting.pk == 1


class TestFileCleanupSignals:
    """register_file_cleanup_signals() (website/models.py) is real, easy-to-
    get-wrong logic — without it, deleted/replaced rows leave orphaned files
    in media/ forever. Brand stands in for every model that uses it
    (ClientLogo, Product, Service, Certification all wire it up the same way)."""

    def test_deleting_a_row_deletes_its_image_file(self, png_upload):
        brand = Brand.objects.create(name='Test Brand', image=png_upload)
        storage = brand.image.storage
        path = brand.image.name

        assert storage.exists(path)
        brand.delete()
        assert not storage.exists(path)

    def test_replacing_the_image_deletes_the_old_file(self, make_png_upload):
        brand = Brand.objects.create(name='Test Brand', image=make_png_upload('first.png'))
        storage = brand.image.storage
        old_path = brand.image.name

        brand.image = make_png_upload('second.png')
        brand.save()

        assert not storage.exists(old_path)
        assert storage.exists(brand.image.name)

    def test_saving_without_changing_the_image_does_not_delete_it(self, png_upload):
        brand = Brand.objects.create(name='Test Brand', image=png_upload)
        path = brand.image.name

        brand.name = 'Renamed Brand'
        brand.save()

        assert brand.image.storage.exists(path)

    def test_creating_a_new_row_does_not_touch_any_existing_file(self, make_png_upload):
        # Regression guard for the on_replace signal's `if not instance.pk`
        # early-return — without it, a brand-new (unsaved) instance would
        # crash trying to look itself up by a pk it doesn't have yet.
        brand = Brand.objects.create(name='Only Brand', image=make_png_upload())
        assert brand.image.storage.exists(brand.image.name)

    def test_deleting_a_certification_deletes_both_its_image_and_pdf_files(self, png_upload, pdf_upload):
        # Certification is the only model with two file-backed fields, each
        # registered with its own register_file_cleanup_signals() call — a
        # regression guard that the second (pdf) registration actually wires
        # up its own post_delete cleanup rather than silently no-op'ing.
        certification = Certification.objects.create(
            name='Test Cert', description='Desc', meta='Meta',
            image=png_upload, pdf=pdf_upload,
        )
        image_storage, image_path = certification.image.storage, certification.image.name
        pdf_storage, pdf_path = certification.pdf.storage, certification.pdf.name

        assert image_storage.exists(image_path)
        assert pdf_storage.exists(pdf_path)
        certification.delete()
        assert not image_storage.exists(image_path)
        assert not pdf_storage.exists(pdf_path)
