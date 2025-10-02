from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("ghl_id", "calendar_id", "contact_id", "start_time", "end_time", "status", "created_at")
    search_fields = ("ghl_id", "calendar_id", "contact_id", "status")
    list_filter = ("status", "calendar_id")
