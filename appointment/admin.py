from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'doctor',
        'patient',
        'appointment_date',
        'start_time',
        'end_time',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'appointment_date',
        'doctor',
    )

    search_fields = (
        'doctor__first_name',
        'doctor__last_name',
        'doctor__medical_system_number',
        'patient__phone',
    )

    ordering = (
        'appointment_date',
        'start_time',
    )