from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


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


@receiver(post_delete, sender=ClientLogo)
def delete_client_logo_file_on_delete(sender, instance, **kwargs):
    # Django never deletes the file backing a FileField/ImageField on its
    # own — without this, every deleted logo leaves an orphaned file in
    # media/client-logos/.
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=ClientLogo)
def delete_client_logo_file_on_replace(sender, instance, **kwargs):
    # Same leak on replace: an edit that uploads a new image would otherwise
    # leave the old file sitting in media/client-logos/ forever.
    if not instance.pk:
        return
    try:
        old_image = ClientLogo.objects.get(pk=instance.pk).image
    except ClientLogo.DoesNotExist:
        return
    if old_image and old_image != instance.image:
        old_image.delete(save=False)


class Brand(models.Model):
    name = models.CharField(max_length=120)
    image = models.ImageField(upload_to='brands/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Brand)
def delete_brand_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)


@receiver(pre_save, sender=Brand)
def delete_brand_file_on_replace(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_image = Brand.objects.get(pk=instance.pk).image
    except Brand.DoesNotExist:
        return
    if old_image and old_image != instance.image:
        old_image.delete(save=False)


class Service(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    icon = models.ImageField(upload_to='services/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


@receiver(post_delete, sender=Service)
def delete_service_icon_on_delete(sender, instance, **kwargs):
    if instance.icon:
        instance.icon.delete(save=False)


@receiver(pre_save, sender=Service)
def delete_service_icon_on_replace(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_icon = Service.objects.get(pk=instance.pk).icon
    except Service.DoesNotExist:
        return
    if old_icon and old_icon != instance.icon:
        old_icon.delete(save=False)


class FireRiskAssessmentItem(models.Model):
    text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.text
