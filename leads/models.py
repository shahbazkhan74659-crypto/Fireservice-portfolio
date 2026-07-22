from django.db import models


class SurveyRequest(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    address = models.TextField(max_length=500)
    problem = models.TextField(max_length=2000)
    why_survey = models.TextField(max_length=2000, verbose_name='Why We Should Survey')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.email}) — {self.created_at:%Y-%m-%d}'


SERVICE_CHOICES = [
    ('fire_detection', 'Fire Detection System'),
    ('co2_gas_flooding', 'Co2 Gas Flooding'),
    ('cctv_pa', 'CCTV & PA System'),
    ('hvws_mvms', 'HVWS / MVMS System'),
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

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.email}) — {self.created_at:%Y-%m-%d}'


class ConsultationRequest(models.Model):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.phone}) — {self.created_at:%Y-%m-%d}'
