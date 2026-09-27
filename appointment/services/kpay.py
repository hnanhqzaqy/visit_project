import requests

from django.conf import settings
from django.urls import reverse


class KPayError(Exception):
    pass


def create_kpay_transaction(
    appointment,
    request,
):
    """
    ایجاد تراکنش واقعی در KPay
    """

    amount_toman = appointment.payable_amount

    if amount_toman <= 0:
        raise KPayError(
            'مبلغ قابل پرداخت معتبر نیست.'
        )

    # KPay مبلغ را به ریال می‌خواهد.
    amount_rial = amount_toman * 10

    callback_url = request.build_absolute_uri(
        reverse(
            'appointment:kpay_callback'
        )
    )

    url = (
        f'{settings.KPAY_BASE_URL}'
        '/transactions/create'
    )

    headers = {
        'Authorization': (
            f'Bearer {settings.KPAY_API_KEY}'
        ),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    payload = {
        'shop_id': settings.KPAY_SHOP_ID,
        'card_id': settings.KPAY_CARD_ID,
        'amount': amount_rial,
        'callback_url': callback_url,
        'description': (
            f'پرداخت نوبت پزشکی '
            f'#{appointment.id}'
        ),
        'factor_number': str(
            appointment.id
        ),
        'fee_side': 'buyer',
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=20,
        )
    except requests.RequestException as exc:
        raise KPayError(
            'ارتباط با KPay برقرار نشد.'
        ) from exc

    if response.status_code not in [200, 201]:
        raise KPayError(
            'خطا در ایجاد تراکنش KPay: '
            f'{response.text}'
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise KPayError(
            'پاسخ KPay قابل پردازش نیست.'
        ) from exc

    payment_url = data.get('payment_url')
    authority = data.get('authority')

    if not payment_url or not authority:
        raise KPayError(
            'KPay اطلاعات کامل تراکنش را برنگرداند.'
        )

    return {
        'id': data.get('id'),
        'authority': authority,
        'amount': data.get('amount'),
        'final_amount': data.get(
            'final_amount'
        ),
        'fee': data.get('fee'),
        'status': data.get('status'),
        'payment_url': payment_url,
    }