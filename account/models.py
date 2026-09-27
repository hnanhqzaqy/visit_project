from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_PATIENT = 'patient'
    ROLE_DOCTOR = 'doctor'

    ROLE_CHOICES = [
        (ROLE_PATIENT, 'بیمار'),
        (ROLE_DOCTOR, 'پزشک'),
    ]

    phone = models.CharField(
        max_length=11,
        unique=True,
        verbose_name='شماره موبایل',
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_PATIENT,
        verbose_name='نقش',
    )

    is_active = models.BooleanField(
        default=False,
        verbose_name='فعال',
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name='کارمند',
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ عضویت',
    )
    objects = UserManager()
    USERNAME_FIELD = 'phone'

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone






class PhoneVerification(models.Model):
    PURPOSE_REGISTER = 'register'
    PURPOSE_PASSWORD_RESET = 'password_reset'

    PURPOSE_CHOICES = [
        (PURPOSE_REGISTER, 'ثبت‌نام'),
        (PURPOSE_PASSWORD_RESET, 'بازیابی رمز عبور'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='phone_verifications',
        verbose_name='کاربر',
    )

    code = models.CharField(
        max_length=6,
        verbose_name='کد تأیید',
    )

    purpose = models.CharField(
        max_length=20,
        choices=PURPOSE_CHOICES,
        verbose_name='هدف کد',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='زمان ایجاد',
    )

    expires_at = models.DateTimeField(
        verbose_name='زمان انقضا',
    )

    is_used = models.BooleanField(
        default=False,
        verbose_name='استفاده شده',
    )

    def __str__(self):
        return f'{self.user.phone} - {self.code}'