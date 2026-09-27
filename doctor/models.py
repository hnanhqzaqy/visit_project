from django.conf import settings
from django.db import models


class Doctor(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    PAYMENT_FULL = 'full'
    PAYMENT_DEPOSIT = 'deposit'

    PAYMENT_POLICY_CHOICES = [
        (PAYMENT_FULL, 'پرداخت کامل'),
        (PAYMENT_DEPOSIT, 'پرداخت ۳۰ درصدی'),
    ]
    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار بررسی'),
        (STATUS_APPROVED, 'تأیید شده'),
        (STATUS_REJECTED, 'رد شده'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
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

    medical_system_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='شماره نظام پزشکی',
    )

    specialty = models.CharField(
        max_length=100,
        verbose_name='تخصص',
    )

    experience_years = models.PositiveIntegerField(
        default=0,
        verbose_name='سابقه کاری',
    )

    bio = models.TextField(
        blank=True,
        verbose_name='معرفی پزشک',
    )

    clinic_address = models.TextField(
        blank=True,
        verbose_name='آدرس مطب',
    )

    profile_image = models.ImageField(
        upload_to='doctors/',
        null=True,
        blank=True,
        verbose_name='تصویر پروفایل',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='وضعیت تأیید',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )
    consultation_fee = models.PositiveBigIntegerField(
        default=0,
        verbose_name='هزینه ویزیت (تومان)',
    )

    payment_policy = models.CharField(
        max_length=20,
        choices=PAYMENT_POLICY_CHOICES,
        default=PAYMENT_FULL,
        verbose_name='روش پرداخت',
    )

    class Meta:
        verbose_name = 'پزشک'
        verbose_name_plural = 'پزشکان'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'





class DoctorSchedule(models.Model):
    DAY_SATURDAY = 5
    DAY_SUNDAY = 6
    DAY_MONDAY = 0
    DAY_TUESDAY = 1
    DAY_WEDNESDAY = 2
    DAY_THURSDAY = 3
    DAY_FRIDAY = 4

    DAY_CHOICES = [
        (DAY_SATURDAY, 'شنبه'),
        (DAY_SUNDAY, 'یکشنبه'),
        (DAY_MONDAY, 'دوشنبه'),
        (DAY_TUESDAY, 'سه‌شنبه'),
        (DAY_WEDNESDAY, 'چهارشنبه'),
        (DAY_THURSDAY, 'پنجشنبه'),
        (DAY_FRIDAY, 'جمعه'),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='پزشک',
    )

    day_of_week = models.PositiveSmallIntegerField(
        choices=DAY_CHOICES,
        verbose_name='روز هفته',
    )

    start_time = models.TimeField(
        verbose_name='ساعت شروع',
    )

    end_time = models.TimeField(
        verbose_name='ساعت پایان',
    )

    appointment_duration = models.PositiveIntegerField(
        default=30,
        verbose_name='مدت هر نوبت به دقیقه',
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
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
        verbose_name = 'برنامه کاری پزشک'
        verbose_name_plural = 'برنامه‌های کاری پزشکان'
        ordering = ['day_of_week', 'start_time']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'day_of_week'],
                name='unique_doctor_schedule_day',
            )
        ]

    def __str__(self):
        day_name = dict(self.DAY_CHOICES).get(self.day_of_week, '')
        return f'{self.doctor} - {day_name}'