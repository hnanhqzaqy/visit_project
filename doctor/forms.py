

from django import forms

from account.models import User
from .models import Doctor, DoctorSchedule


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'first_name',
            'last_name',
            'medical_system_number',
            'specialty',
            'experience_years',
            'consultation_fee',
            'payment_policy',
            'bio',
            'clinic_address',
            'profile_image',
        ]
        widgets = {
            'bio': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'درباره خود، تخصص و تجربه کاری‌تان بنویسید.',
                }
            ),
            'clinic_address': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'آدرس مطب خود را وارد کنید.',
                }
            ),
            'profile_image': forms.FileInput(
                attrs={
                    'accept': 'image/*',
                }
            ),
            'consultation_fee': forms.NumberInput(
                attrs={
                    'min': 0,
                    'placeholder': 'مثلاً ۶۰۰۰۰۰',
                }
            ),
            'payment_policy': forms.Select(),
        }

    def clean_medical_system_number(self):
        value = self.cleaned_data['medical_system_number'].strip()

        if not value.isdigit():
            raise forms.ValidationError(
                'شماره نظام پزشکی باید فقط شامل اعداد باشد.'
            )

        return value

    def clean_experience_years(self):
        value = self.cleaned_data['experience_years']

        if value < 0:
            raise forms.ValidationError(
                'سابقه کاری نمی‌تواند منفی باشد.'
            )

        if value > 80:
            raise forms.ValidationError(
                'مقدار سابقه کاری واردشده معتبر نیست.'
            )

        return value

    def clean_consultation_fee(self):
        value = self.cleaned_data['consultation_fee']

        if value <= 0:
            raise forms.ValidationError(
                'هزینه ویزیت باید بیشتر از صفر باشد.'
            )

        return value


class DoctorRegisterForm(forms.Form):
    phone = forms.CharField(
        label='شماره موبایل',
        max_length=11,
    )

    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput,
        min_length=8,
    )

    password_confirm = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput,
    )

    first_name = forms.CharField(
        label='نام',
        max_length=100,
    )

    last_name = forms.CharField(
        label='نام خانوادگی',
        max_length=100,
    )

    medical_system_number = forms.CharField(
        label='شماره نظام پزشکی',
        max_length=20,
    )

    specialty = forms.CharField(
        label='تخصص',
        max_length=100,
    )

    experience_years = forms.IntegerField(
        label='سابقه کاری به سال',
        min_value=0,
        max_value=80,
    )

    bio = forms.CharField(
        label='معرفی پزشک',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': 'درباره خود و تجربه کاری‌تان بنویسید.',
            }
        ),
    )

    clinic_address = forms.CharField(
        label='آدرس مطب',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'placeholder': 'آدرس مطب خود را وارد کنید.',
            }
        ),
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                'شماره موبایل باید فقط شامل اعداد باشد.'
            )

        if len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError(
                'شماره موبایل باید به صورت 09xxxxxxxxx باشد.'
            )

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                'این شماره موبایل قبلاً ثبت شده است.'
            )

        return phone

    def clean_medical_system_number(self):
        value = self.cleaned_data['medical_system_number'].strip()

        if not value.isdigit():
            raise forms.ValidationError(
                'شماره نظام پزشکی باید فقط شامل اعداد باشد.'
            )

        if Doctor.objects.filter(
            medical_system_number=value
        ).exists():
            raise forms.ValidationError(
                'این شماره نظام پزشکی قبلاً ثبت شده است.'
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if (
            password
            and password_confirm
            and password != password_confirm
        ):
            self.add_error(
                'password_confirm',
                'تکرار رمز عبور با رمز عبور یکسان نیست.',
            )

        return cleaned_data


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule
        fields = [
            'day_of_week',
            'start_time',
            'end_time',
            'appointment_duration',
            'is_active',
        ]
        widgets = {
            'start_time': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'},
            ),
            'end_time': forms.TimeInput(
                format='%H:%M',
                attrs={'type': 'time'},
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                'ساعت پایان باید بعد از ساعت شروع باشد.'
            )

        return cleaned_data

    def clean_appointment_duration(self):
        value = self.cleaned_data['appointment_duration']

        if value <= 0:
            raise forms.ValidationError(
                'مدت هر نوبت باید بیشتر از صفر باشد.'
            )

        if value > 180:
            raise forms.ValidationError(
                'مدت هر نوبت نمی‌تواند بیشتر از ۱۸۰ دقیقه باشد.'
            )

        return value


class DoctorRegisterForm(forms.Form):
    phone = forms.CharField(
        label='شماره موبایل',
        max_length=11
    )

    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput,
        min_length=8
    )

    password_confirm = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput
    )

    first_name = forms.CharField(
        label='نام',
        max_length=100
    )

    last_name = forms.CharField(
        label='نام خانوادگی',
        max_length=100
    )

    medical_system_number = forms.CharField(
        label='شماره نظام پزشکی',
        max_length=20
    )

    specialty = forms.CharField(
        label='تخصص',
        max_length=100
    )

    experience_years = forms.IntegerField(
        label='سابقه کاری به سال',
        min_value=0,
        max_value=80
    )

    bio = forms.CharField(
        label='معرفی پزشک',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': 'درباره خود و تجربه کاری‌تان بنویسید.',
            }
        )
    )

    clinic_address = forms.CharField(
        label='آدرس مطب',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 4,
                'placeholder': 'آدرس مطب خود را وارد کنید.',
            }
        )
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()

        if not phone.isdigit():
            raise forms.ValidationError(
                'شماره موبایل باید فقط شامل اعداد باشد.'
            )

        if len(phone) != 11 or not phone.startswith('09'):
            raise forms.ValidationError(
                'شماره موبایل باید به صورت 09xxxxxxxxx باشد.'
            )

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                'این شماره موبایل قبلاً ثبت شده است.'
            )

        return phone

    def clean_medical_system_number(self):
        value = self.cleaned_data['medical_system_number'].strip()

        if not value.isdigit():
            raise forms.ValidationError(
                'شماره نظام پزشکی باید فقط شامل اعداد باشد.'
            )

        if Doctor.objects.filter(
            medical_system_number=value
        ).exists():
            raise forms.ValidationError(
                'این شماره نظام پزشکی قبلاً ثبت شده است.'
            )

        return value

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if (
            password
            and password_confirm
            and password != password_confirm
        ):
            self.add_error(
                'password_confirm',
                'تکرار رمز عبور با رمز عبور یکسان نیست.'
            )

        return cleaned_data


class DoctorScheduleForm(forms.ModelForm):
    class Meta:
        model = DoctorSchedule

        fields = [
            'day_of_week',
            'start_time',
            'end_time',
            'appointment_duration',
            'is_active',
        ]

        widgets = {
            'start_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time',
                }
            ),
            'end_time': forms.TimeInput(
                format='%H:%M',
                attrs={
                    'type': 'time',
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()

        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise forms.ValidationError(
                'ساعت پایان باید بعد از ساعت شروع باشد.'
            )

        return cleaned_data

    def clean_appointment_duration(self):
        value = self.cleaned_data['appointment_duration']

        if value <= 0:
            raise forms.ValidationError(
                'مدت هر نوبت باید بیشتر از صفر باشد.'
            )

        if value > 180:
            raise forms.ValidationError(
                'مدت هر نوبت نمی‌تواند بیشتر از ۱۸۰ دقیقه باشد.'
            )

        return value