import jdatetime
from django import forms

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    appointment_date = forms.CharField(
        label='تاریخ نوبت',
        widget=forms.HiddenInput(
            attrs={
                'id': 'appointment-date',
            }
        )
    )

    start_time = forms.CharField(
        label='ساعت شروع',
        widget=forms.HiddenInput(
            attrs={
                'id': 'start-time',
            }
        )
    )

    class Meta:
        model = Appointment
        fields = [
            'appointment_date',
            'start_time',
            'patient_note',
        ]

        widgets = {
            'patient_note': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'در صورت نیاز توضیحات خود را وارد کنید.',
                }
            ),
        }

    def clean_appointment_date(self):
        value = self.cleaned_data['appointment_date'].strip()

        try:
            year, month, day = map(int, value.split('/'))

            jalali_date = jdatetime.date(
                year,
                month,
                day,
            )

            return jalali_date.togregorian()

        except (ValueError, TypeError):
            raise forms.ValidationError(
                'تاریخ انتخاب‌شده معتبر نیست.'
            )

    def clean_start_time(self):
        value = self.cleaned_data['start_time'].strip()

        try:
            hour, minute = map(int, value.split(':'))

            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError

            from datetime import time

            return time(hour, minute)

        except (ValueError, TypeError):
            raise forms.ValidationError(
                'ساعت انتخاب‌شده معتبر نیست.'
            )