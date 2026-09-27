from django.db import models

from appointment.models import Appointment


class Visit(models.Model):

    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.CASCADE,
        related_name='visit',
        verbose_name='نوبت',
    )

    patient_complaint = models.TextField(
        verbose_name='شکایت اصلی بیمار',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد',
    )

    class Meta:
        verbose_name = 'ویزیت'
        verbose_name_plural = 'ویزیت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return (
            f'ویزیت '
            f'{self.appointment.patient} - '
            f'{self.appointment.appointment_date}'
        )