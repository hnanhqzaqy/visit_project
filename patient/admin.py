from django.contrib import admin

from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = (
        'first_name',
        'last_name',
        'user',
        'national_code',
        'gender',
        'created_at',
    )

    list_filter = (
        'gender',
        'created_at',
    )

    search_fields = (
        'first_name',
        'last_name',
        'national_code',
        'user__phone',
    )