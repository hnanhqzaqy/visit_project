import jdatetime
from django import forms

from .models import Patient


class PatientProfileForm(forms.ModelForm):

    birth_date = forms.CharField(
        label='تاریخ تولد',
        required=False,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'مثلاً 1380/05/15',
                'autocomplete': 'off',
            }
        ),
    )

    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'national_code',
            'birth_date',
            'gender',
            'address',
            'profile_image',
        ]

        widgets = {
            'address': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'آدرس خود را وارد کنید',
                }
            ),
            'profile_image': forms.FileInput(
                attrs={
                    'accept': 'image/*',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # فارسی کردن گزینه پیش‌فرض جنسیت
        self.fields['gender'].choices = [
            ('', 'انتخاب جنسیت')
        ] + list(Patient.GENDER_CHOICES)

        # نمایش تاریخ ذخیره‌شده به صورت شمسی
        if self.instance and self.instance.birth_date:
            jalali_date = jdatetime.date.fromgregorian(
                date=self.instance.birth_date
            )

            self.initial['birth_date'] = jalali_date.strftime(
                '%Y/%m/%d'
            )

    def clean_national_code(self):
        national_code = self.cleaned_data.get('national_code')

        if not national_code:
            return national_code

        national_code = national_code.strip()

        if not national_code.isdigit():
            raise forms.ValidationError(
                'کد ملی باید فقط شامل اعداد باشد.'
            )

        if len(national_code) != 10:
            raise forms.ValidationError(
                'کد ملی باید ۱۰ رقم باشد.'
            )

        return national_code

    def clean_birth_date(self):
        value = (self.cleaned_data.get('birth_date') or '').strip()

        if not value:
            return None

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
                'تاریخ تولد را به صورت ۱۴۰۰/۰۵/۱۵ وارد کنید.'
            )