from datetime import timedelta
import random

from django.utils import timezone

from .models import PhoneVerification
from core.services.kpanel import send_sms, KPanelError


VERIFICATION_CODE_EXPIRY_MINUTES = 2
RESEND_COOLDOWN_SECONDS = 120


def generate_verification_code():
    return str(random.randint(100000, 999999))


def create_phone_verification(user, purpose):
    code = generate_verification_code()

    PhoneVerification.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False,
    ).update(
        is_used=True
    )

    verification = PhoneVerification.objects.create(
        user=user,
        code=code,
        purpose=purpose,
        expires_at=(
            timezone.now()
            + timedelta(
                minutes=VERIFICATION_CODE_EXPIRY_MINUTES
            )
        ),
    )

    return verification


def can_resend_verification(user, purpose):
    last_verification = (
        PhoneVerification.objects
        .filter(
            user=user,
            purpose=purpose,
        )
        .order_by('-created_at')
        .first()
    )

    if not last_verification:
        return True

    elapsed_seconds = (
        timezone.now() - last_verification.created_at
    ).total_seconds()

    return elapsed_seconds >= RESEND_COOLDOWN_SECONDS


def resend_phone_verification(user, purpose):
    if not can_resend_verification(user, purpose):
        return None

    return create_phone_verification(
        user=user,
        purpose=purpose,
    )


def send_verification_sms(user, verification):
    if verification.purpose == PhoneVerification.PURPOSE_REGISTER:
        message = (
            'سیستم نوبت‌دهی پزشکی\n'
            f'کد تأیید ثبت‌نام شما: {verification.code}'
        )

    elif verification.purpose == PhoneVerification.PURPOSE_PASSWORD_RESET:
        message = (
            'سیستم نوبت‌دهی پزشکی\n'
            f'کد بازیابی رمز عبور شما: {verification.code}'
        )

    else:
        message = (
            'سیستم نوبت‌دهی پزشکی\n'
            f'کد تأیید شما: {verification.code}'
        )

    try:
        return send_sms(
            to=user.phone,
            message=message,
        )
    except KPanelError:
        return None