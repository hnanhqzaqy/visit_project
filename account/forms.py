from django import forms

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput,
        min_length=8,
    )

    password_confirm = forms.CharField(
        label='تکرار رمز عبور',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ['phone', 'password', 'password_confirm']

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

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error(
                'password_confirm',
                'تکرار رمز عبور با رمز عبور یکسان نیست.'
            )

        return cleaned_data




class PhoneVerificationForm(forms.Form):
    code = forms.CharField(
        label='کد تأیید',
        max_length=6,
        min_length=6,
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()

        if not code.isdigit():
            raise forms.ValidationError(
                'کد تأیید باید فقط شامل اعداد باشد.'
            )

        return code



class LoginForm(forms.Form):
    phone = forms.CharField(
        label='شماره موبایل',
        max_length=11,
    )

    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput,
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

        return phone



class ForgotPasswordForm(forms.Form):
    phone = forms.CharField(
        label='شماره موبایل',
        max_length=11,
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

        if not User.objects.filter(phone=phone).exists():
            raise forms.ValidationError(
                'کاربری با این شماره موبایل پیدا نشد.'
            )

        return phone






class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput,
        min_length=8,
    )

    password_confirm = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm and password != password_confirm:
            self.add_error(
                'password_confirm',
                'تکرار رمز عبور با رمز عبور جدید یکسان نیست.'
            )

        return cleaned_data