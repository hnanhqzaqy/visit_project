from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import (
    ForgotPasswordForm,
    LoginForm,
    PhoneVerificationForm,
    RegisterForm,
    ResetPasswordForm,
)
from .models import PhoneVerification, User
from .services import (
    create_phone_verification,
    resend_phone_verification,
    send_verification_sms,
)


def register(request):
    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = False
        user.save()

        verification = create_phone_verification(
            user=user,
            purpose=PhoneVerification.PURPOSE_REGISTER,
        )

        request.session['verification_user_id'] = user.id

        sms_result = send_verification_sms(
            user=user,
            verification=verification,
        )

        if sms_result is None:
            messages.error(
                request,
                'ارسال کد تأیید با خطا مواجه شد. لطفاً دوباره تلاش کنید.',
            )
            return redirect('account:verify_phone')

        messages.success(
            request,
            'کد تأیید به شماره موبایل شما ارسال شد.',
        )

        return redirect('account:verify_phone')

    return render(
        request,
        'account/register.html',
        {'form': form},
    )


def verify_phone(request):
    user_id = request.session.get('verification_user_id')

    if not user_id:
        return redirect('account:register')

    user = get_object_or_404(User, id=user_id)

    form = PhoneVerificationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        verification = PhoneVerification.objects.filter(
            user=user,
            code=form.cleaned_data['code'],
            purpose=PhoneVerification.PURPOSE_REGISTER,
            is_used=False,
        ).order_by('-created_at').first()

        if not verification:
            form.add_error(
                'code',
                'کد تأیید اشتباه است.'
            )

        elif verification.expires_at < timezone.now():
            form.add_error(
                'code',
                'کد تأیید منقضی شده است.'
            )

        else:
            verification.is_used = True
            verification.save(update_fields=['is_used'])

            user.is_active = True
            user.save(update_fields=['is_active'])

            request.session.pop('verification_user_id', None)

            messages.success(
                request,
                'شماره موبایل شما با موفقیت تأیید شد.',
            )

            return redirect('account:login')

    return render(
        request,
        'account/verify_phone.html',
        {'form': form},
    )


def resend_register_code(request):
    user_id = request.session.get('verification_user_id')

    if not user_id:
        return redirect('account:register')

    user = get_object_or_404(User, id=user_id)

    verification = resend_phone_verification(
        user=user,
        purpose=PhoneVerification.PURPOSE_REGISTER,
    )

    if verification is None:
        messages.warning(
            request,
            'کد قبلی هنوز معتبر است. لطفاً یک دقیقه صبر کنید.',
        )

        return redirect('account:verify_phone')

    sms_result = send_verification_sms(
        user=user,
        verification=verification,
    )

    if sms_result is None:
        messages.error(
            request,
            'ارسال کد تأیید با خطا مواجه شد.',
        )
        return redirect('account:verify_phone')

    messages.success(
        request,
        'کد تأیید با موفقیت ارسال شد.',
    )

    return redirect('account:verify_phone')


def login_view(request):
    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        phone = form.cleaned_data['phone']
        password = form.cleaned_data['password']

        user = authenticate(
            request,
            phone=phone,
            password=password,
        )

        if user is None:
            form.add_error(
                None,
                'شماره موبایل یا رمز عبور اشتباه است.'
            )
        else:
            login(request, user)

            if user.is_staff:
                return redirect('admin_panel:dashboard')

            if getattr(user, 'role', None) == 'patient':
                return redirect('patient:dashboard')

            if getattr(user, 'role', None) == 'doctor':
                return redirect('doctor:dashboard')

            return redirect('core:home')

    return render(
        request,
        'account/login.html',
        {'form': form},
    )


def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        phone = form.cleaned_data['phone']

        user = User.objects.filter(
            phone=phone
        ).first()

        if user:
            verification = create_phone_verification(
                user=user,
                purpose=PhoneVerification.PURPOSE_PASSWORD_RESET,
            )

            request.session['password_reset_user_id'] = user.id

            sms_result = send_verification_sms(
                user=user,
                verification=verification,
            )

            if sms_result is None:
                messages.error(
                    request,
                    'ارسال کد بازیابی با خطا مواجه شد.',
                )
            else:
                messages.success(
                    request,
                    'کد بازیابی به شماره موبایل شما ارسال شد.',
                )

        return redirect('account:verify_reset_code')

    return render(
        request,
        'account/forgot_password.html',
        {'form': form},
    )


def verify_reset_code(request):
    user_id = request.session.get('password_reset_user_id')

    if not user_id:
        return redirect('account:forgot_password')

    user = get_object_or_404(User, id=user_id)

    form = PhoneVerificationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        verification = PhoneVerification.objects.filter(
            user=user,
            code=form.cleaned_data['code'],
            purpose=PhoneVerification.PURPOSE_PASSWORD_RESET,
            is_used=False,
        ).order_by('-created_at').first()

        if not verification:
            form.add_error(
                'code',
                'کد تأیید اشتباه است.'
            )

        elif verification.expires_at < timezone.now():
            form.add_error(
                'code',
                'کد تأیید منقضی شده است.'
            )

        else:
            verification.is_used = True
            verification.save(update_fields=['is_used'])

            request.session['reset_code_verified'] = True

            return redirect('account:reset_password')

    return render(
        request,
        'account/verify_reset_code.html',
        {'form': form},
    )


def resend_reset_code(request):
    user_id = request.session.get('password_reset_user_id')

    if not user_id:
        return redirect('account:forgot_password')

    user = get_object_or_404(User, id=user_id)

    verification = resend_phone_verification(
        user=user,
        purpose=PhoneVerification.PURPOSE_PASSWORD_RESET,
    )

    if verification is None:
        messages.warning(
            request,
            'کد قبلی هنوز معتبر است. لطفاً یک دقیقه صبر کنید.',
        )

        return redirect('account:verify_reset_code')

    sms_result = send_verification_sms(
        user=user,
        verification=verification,
    )

    if sms_result is None:
        messages.error(
            request,
            'ارسال کد بازیابی با خطا مواجه شد.',
        )
        return redirect('account:verify_reset_code')

    messages.success(
        request,
        'کد بازیابی با موفقیت ارسال شد.',
    )

    return redirect('account:verify_reset_code')


def reset_password(request):
    user_id = request.session.get('password_reset_user_id')
    code_verified = request.session.get('reset_code_verified')

    if not user_id or not code_verified:
        return redirect('account:forgot_password')

    user = get_object_or_404(User, id=user_id)

    form = ResetPasswordForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user.set_password(form.cleaned_data['password'])
        user.save(update_fields=['password'])

        request.session.pop('password_reset_user_id', None)
        request.session.pop('reset_code_verified', None)

        messages.success(
            request,
            'رمز عبور شما با موفقیت تغییر کرد.',
        )

        return redirect('account:login')

    return render(
        request,
        'account/reset_password.html',
        {'form': form},
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        'با موفقیت از حساب کاربری خارج شدید.',
    )

    return redirect('core:home')