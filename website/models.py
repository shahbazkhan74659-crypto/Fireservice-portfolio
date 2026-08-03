from django.db import models
from django.db.models.signals import post_delete, pre_save


def register_file_cleanup_signals(model, field_name='image', with_replace=True):
    """Wires up file-cleanup signal receivers for a model with an
    ImageField/FileField named `field_name`. Django never deletes the file
    backing a FileField/ImageField on its own — without this, every deleted
    row (post_delete) or replaced image (pre_save) leaves an orphaned file
    in media/.

    Used by ClientLogo/Brand/Product (field_name='image') and Service
    (field_name='icon') with `with_replace=True` (they all support Edit, so
    a "replace" case needs guarding); Certification passes
    `with_replace=False` since it has no Edit, so there's no replace case —
    only post_delete cleanup applies there.

    `weak=False` is required here (unlike Django's `@receiver` decorator
    default) because these receivers are closures created inside this
    factory rather than module-level functions — without a strong
    reference, Python's garbage collector could reclaim them and silently
    disconnect the signal.
    """

    def on_delete(sender, instance, **kwargs):
        file = getattr(instance, field_name)
        if file:
            file.delete(save=False)

    post_delete.connect(on_delete, sender=model, weak=False)

    if not with_replace:
        return

    def on_replace(sender, instance, **kwargs):
        if not instance.pk:
            return
        try:
            old_instance = model.objects.get(pk=instance.pk)
        except model.DoesNotExist:
            return
        old_file = getattr(old_instance, field_name)
        new_file = getattr(instance, field_name)
        if old_file and old_file != new_file:
            old_file.delete(save=False)

    pre_save.connect(on_replace, sender=model, weak=False)


class MissionVisionItem(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField()
    points = models.JSONField(default=list, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class ClientLogo(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='client-logos/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


register_file_cleanup_signals(ClientLogo)


class Brand(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='brands/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


register_file_cleanup_signals(Brand)


class Service(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.ImageField(upload_to='services/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


register_file_cleanup_signals(Service, field_name='icon')


class Product(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


register_file_cleanup_signals(Product)


class ProcessPhase(models.Model):
    # `name` doubles as the image's alt text on the Process page (same
    # convention as Product/Brand/ClientLogo's `name`), not a phase title —
    # `title`/`tagline` hold the visible h3/subtitle copy. The Process page
    # loops over this model entirely (see process.html), so every phase's
    # full content — image, title, tagline and both explanation cards —
    # lives here; adding/removing a row changes how many phases render.
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='process-phases/')
    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=200, default='')
    tagline = models.CharField(max_length=200, default='')
    card1_title = models.CharField(max_length=200, default='')
    card1_text = models.TextField(default='')
    card2_title = models.CharField(max_length=200, default='')
    card2_text = models.TextField(default='')

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


register_file_cleanup_signals(ProcessPhase)


class HeroSlide(models.Model):
    # Backs includes/hero-bg-slideshow.html, reused on the Home hero, the
    # About page's Mission & Vision section and the Services page's cards
    # background — one shared DB-driven slideshow, no per-page image sets.
    # No alt text: these render as CSS background-image layers, not <img>
    # tags, so they're decorative.
    image = models.ImageField(upload_to='hero-slides/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'Hero Slide {self.order}'


register_file_cleanup_signals(HeroSlide)


class Certification(models.Model):
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=200)
    meta = models.CharField(max_length=200)
    # Always populated — either uploaded directly, or auto-rendered from
    # `pdf`'s first page (see CertificationSerializer.create()) — so every
    # template can keep just rendering `image` unconditionally.
    image = models.ImageField(upload_to='certifications/')
    # Optional: only set when the admin uploaded a PDF instead of an image.
    # When present, "View Full Certificate" links here instead of `image`.
    pdf = models.FileField(upload_to='certifications/pdfs/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


register_file_cleanup_signals(Certification, with_replace=False)
register_file_cleanup_signals(Certification, field_name='pdf', with_replace=False)


class SiteSetting(models.Model):
    # Singleton row (always pk=1) for small sitewide values that don't need
    # their own model+list UI — currently the "10+ Years Experience" figure
    # shown in every stats bar (Home/About/Consultation/Clientele) and the
    # Home page's Clients Served / Installations / Emergency Support hero
    # stats, and the About page's "Team Members" stat.
    years_experience = models.PositiveIntegerField(default=10)
    clients_served = models.PositiveIntegerField(default=0)
    installations = models.PositiveIntegerField(default=0)
    emergency_support = models.PositiveIntegerField(default=0)
    team_members = models.PositiveIntegerField(default=0)
    # Crossfade interval for every includes/hero-bg-slideshow.html instance
    # (Home hero, About Mission & Vision, Services cards) — read by site.js
    # via a data attribute rendered onto .hero__bg, not hardcoded per page.
    hero_slide_duration_seconds = models.PositiveIntegerField(default=5)

    class Meta:
        # Without this, Django's default CamelCase-to-words split renders as
        # all-lowercase "site setting" / "site settings" in admin (e.g. the
        # changelist footer's "1 site setting").
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Site Settings'


class Brochure(models.Model):
    # Singleton row (always pk=1), same convention as SiteSetting — there's
    # only ever one current company brochure PDF, linked from the nav's "Get
    # Brochure" button and the /brochure/ page itself.
    pdf = models.FileField(upload_to='brochure/')
    # Auto-rendered from `pdf`'s first page (BrochureSerializer, same
    # render_pdf_first_page_to_png() Certification uses) — the Admin Hub's
    # Brochure modal shows this as a preview instead of embedding the PDF.
    image = models.ImageField(upload_to='brochure/', default='')

    class Meta:
        verbose_name = 'Brochure'
        verbose_name_plural = 'Brochure'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return 'Brochure'


register_file_cleanup_signals(Brochure, field_name='pdf')
register_file_cleanup_signals(Brochure, field_name='image')


class FireRiskAssessmentItem(models.Model):
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text
