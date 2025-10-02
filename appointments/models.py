from django.db import models

class Appointment(models.Model):
    ghl_id = models.CharField(max_length=100, unique=True)
    calendar_id = models.CharField(max_length=100)
    contact_id = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=50, default="confirmed")
    raw = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ghl_id} ({self.status})"
