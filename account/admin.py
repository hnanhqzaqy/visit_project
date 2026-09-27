from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    ordering = ('phone',)

    list_display = (
        'phone',
        'role',
        'is_active',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
    )

    search_fields = (
        'phone',
    )

    fieldsets = (
        (None, {
            'fields': (
                'phone',
                'password',
            )
        }),
        ('اطلاعات حساب', {
            'fields': (
                'role',
                'is_active',
                'is_staff',
            )
        }),
        ('دسترسی‌ها', {
            'fields': (
                'groups',
                'user_permissions',
            )
        }),
        ('تاریخ‌ها', {
            'fields': (
                'last_login',
                'date_joined',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'phone',
                'password1',
                'password2',
                'role',
                'is_active',
                'is_staff',
            ),
        }),
    )