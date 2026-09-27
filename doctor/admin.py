from django.contrib import admin
from .models import Doctor, DoctorSchedule




@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'medical_system_number',
        'specialty',
        'experience_years',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'specialty',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'medical_system_number',
        'specialty',
        'user__phone',
    )






@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = (
        'doctor',
        'day_of_week',
        'start_time',
        'end_time',
        'appointment_duration',
        'is_active',
    )

    list_filter = (
        'day_of_week',
        'is_active',
    )

    search_fields = (
        'doctor__first_name',
        'doctor__last_name',
        'doctor__medical_system_number',
    )