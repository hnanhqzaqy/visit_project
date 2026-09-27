from django.conf import settings
from django.db import models

from doctor.models import Doctor


class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار تأیید'),
        (STATUS_CONFIRMED, 'تأیید شده'),
        (STATUS_CANCELLED, 'لغو شده'),
        (STATUS_COMPLETED, 'انجام شده'),
    ]

    PAYMENT_PENDING = 'pending'
    PAYMENT_PARTIAL = 'partial'
    PAYMENT_PAID = 'paid'
    PAYMENT_FAILED = 'failed'
    PAYMENT_REFUNDED = 'refunded'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'پرداخت نشده'),
        (PAYMENT_PARTIAL, 'پرداخت بخشی'),
        (PAYMENT_PAID, 'پرداخت کامل'),
        (PAYMENT_FAILED, 'پرداخت ناموفق'),
        (PAYMENT_REFUNDED, 'بازپرداخت شده'),
    ]

    PAYMENT_FULL = 'full'
    PAYMENT_DEPOSIT = 'deposit'

    PAYMENT_POLICY_CHOICES = [
        (PAYMENT_FULL, 'پرداخت کامل'),
        (PAYMENT_DEPOSIT, 'پرداخت ۳۰ درصدی'),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='پزشک',
    )

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='بیمار',
    )

    appointment_date = models.DateField(
        verbose_name='تاریخ نوبت',
    )

    start_time = models.TimeField(
        verbose_name='ساعت شروع',
    )

    end_time = models.TimeField(
        verbose_name='ساعت پایان',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='وضعیت',
    )

    patient_note = models.TextField(
        blank=True,
        verbose_name='توضیحات بیمار',
    )

    # اطلاعات مالی نوبت
    payment_policy = models.CharField(
        max_length=20,
        choices=PAYMENT_POLICY_CHOICES,
        default=PAYMENT_FULL,
        verbose_name='روش پرداخت',
    )

    total_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ کل ویزیت (تومان)',
    )

    payable_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ قابل پرداخت آنلاین (تومان)',
    )

    paid_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ پرداخت‌شده (تومان)',
    )

    remaining_amount = models.PositiveBigIntegerField(
        default=0,
        verbose_name='مبلغ باقی‌مانده (تومان)',
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default=PAYMENT_PENDING,
        verbose_name='وضعیت پرداخت',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ثبت',
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='آخرین بروزرسانی',
    )

    class Meta:
        verbose_name = 'نوبت'
        verbose_name_plural = 'نوبت‌ها'
        ordering = ['appointment_date', 'start_time']

    def __str__(self):
        return f'{self.doctor} - {self.appointment_date} - {self.start_time}'



class Payment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'در انتظار پرداخت'),
        (STATUS_UNDER_REVIEW, 'در انتظار بررسی'),
        (STATUS_SUCCESS, 'پرداخت تأیید شده'),
        (STATUS_FAILED, 'پرداخت رد شده'),
    ]

    appointment = models.ForeignKey(
        Appointment,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='نوبت',
    )

    amount = models.PositiveBigIntegerField(
        verbose_name='مبلغ پرداخت (تومان)',
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='وضعیت پرداخت',
    )

    receipt_image = models.ImageField(
        upload_to='payment_receipts/',
        null=True,
        blank=True,
        verbose_name='تصویر رسید پرداخت',
    )

    tracking_code = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='شماره پیگیری',
    )

    authority = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='شناسه پرداخت درگاه',
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='شماره تراکنش',
    )

    review_note = models.TextField(
        blank=True,
        verbose_name='توضیحات بررسی',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ ارسال رسید',
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ بررسی',
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ تأیید پرداخت',
    )

    class Meta:
        verbose_name = 'تراکنش پرداخت'
        verbose_name_plural = 'تراکنش‌های پرداخت'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'{self.appointment} - '
            f'{self.amount} تومان - '
            f'{self.get_status_display()}'
        )