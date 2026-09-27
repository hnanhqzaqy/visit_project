import requests

from django.conf import settings


class KPanelError(Exception):
    pass


def send_sms(to, message):
    url = 'https://edge.ippanel.com/v1/api/send/webservice'

    payload = {
        'from': settings.KPANEL_FROM,
        'message': message,
        'to': to,
        'username': settings.KPANEL_USERNAME,
        'password': settings.KPANEL_PASSWORD,
    }

    try:
        response = requests.get(
            url,
            params=payload,
            timeout=20,
        )
    except requests.RequestException as exc:
        raise KPanelError(
            'ارتباط با سامانه پیامکی کاپنل برقرار نشد.'
        ) from exc

    result = response.text.strip()

    if not response.ok:
        raise KPanelError(
            f'خطا در ارتباط با کاپنل: {result}'
        )

    return result