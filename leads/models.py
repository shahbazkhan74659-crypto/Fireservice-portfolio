from django.db import models


class SurveyRequest(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    address = models.TextField(max_length=500)
    problem = models.TextField(max_length=2000)
    why_survey = models.TextField(max_length=2000, verbose_name='Why We Should Survey')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.email}) — {self.created_at:%Y-%m-%d}'


SERVICE_CHOICES = [
    ('fire_detection', 'Fire Detection System'),
    ('co2_gas_flooding', 'Co2 Gas Flooding'),
    ('cctv_pa', 'CCTV & PA System'),
    ('hvws_mvms', 'HVWS / MVWS System'),
    ('fire_extinguisher', 'All Type Fire Extinguisher'),
    ('safety_equipment', 'Safety Equipment'),
    ('fire_pump_house', 'Fire Pump House'),
    ('electricals', 'All Type Electricals Work'),
    ('other', 'Not sure / Other'),
]


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    service = models.CharField(max_length=30, choices=SERVICE_CHOICES, default='other')
    message = models.TextField(max_length=2000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.email}) — {self.created_at:%Y-%m-%d}'


class ConsultationRequest(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.phone}) — {self.created_at:%Y-%m-%d}'


class LeadNotificationCounter(models.Model):
    """Singleton row (always pk=1, same idiom as website.models.SiteSetting)
    tallying new-lead *creation* events since the last bundled admin
    notification email fired — split per lead type so the email can report
    a breakdown. Deliberately unrelated to resolved/resolved_at: this counts
    creations only. See leads/services.py's
    record_lead_created_and_maybe_notify() for the increment-and-maybe-fire
    logic and website.models.SiteSetting.lead_notification_threshold for the
    admin-configurable threshold."""
    survey_count = models.PositiveIntegerField(default=0)
    contact_count = models.PositiveIntegerField(default=0)
    consultation_count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Lead Notification Counter'
        verbose_name_plural = 'Lead Notification Counter'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def total(self):
        return self.survey_count + self.contact_count + self.consultation_count

    def __str__(self):
        return f'Lead Notification Counter ({self.total} pending)'
