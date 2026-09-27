from django.conf import settings
from django.db import models


class Patient(models.Model):
    GENDER_MALE = 'male'
    GENDER_FEMALE = 'female'

    GENDER_CHOICES = [
        (GENDER_MALE, 'مرد'),
        (GENDER_FEMALE, 'زن'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name='کاربر',
    )

    first_name = models.CharField(
        max_length=100,
        verbose_name='نام',
    )

    last_name = models.CharField(
        max_length=100,
        verbose_name='نام خانوادگی',
    )

    national_code = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        verbose_name='کد ملی',
    )

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='تاریخ تولد',
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name='جنسیت',
    )

    address = models.TextField(
        blank=True,
        verbose_name='آدرس',
    )

    profile_image = models.ImageField(
        upload_to='patients/',
        null=True,
        blank=True,
        verbose_name='تصویر پروفایل',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'بیمار'
        verbose_name_plural = 'بیماران'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'