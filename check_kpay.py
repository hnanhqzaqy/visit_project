import environ
import requests
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

mobile = env('KPAY_MOBILE')
password = env('KPAY_PASSWORD')

base_url = 'https://kpay.website/api/v1'


print('در حال ورود به حساب KPay...')

login_response = requests.post(
    f'{base_url}/auth/login',
    data={
        'username': mobile,
        'password': password,
    },
    timeout=15,
)

print('\n--- LOGIN RESPONSE ---')
print('Status:', login_response.status_code)
print(login_response.text)


if login_response.status_code != 200:
    print('\nورود به KPay ناموفق بود.')
    raise SystemExit


access_token = login_response.json().get('access_token')

if not access_token:
    print('\nAccess Token دریافت نشد.')
    raise SystemExit


headers = {
    'Authorization': f'Bearer {access_token}',
    'Accept': 'application/json',
}


print('\nدر حال دریافت فروشگاه‌ها...')

shops_response = requests.get(
    f'{base_url}/shops',
    headers=headers,
    timeout=15,
)

print('\n--- SHOP RESPONSE ---')
print('Status:', shops_response.status_code)
print(shops_response.text)


print('\nدر حال دریافت کارت‌ها...')

cards_response = requests.get(
    f'{base_url}/cards',
    headers=headers,
    timeout=15,
)

print('\n--- CARD RESPONSE ---')
print('Status:', cards_response.status_code)
print(cards_response.text)







print("\nSHOP IDS:")

shops_data = shops_response.json()

for shop in shops_data.get("shops", []):
    print("Shop Name:", shop.get("name"))
    print("Shop ID:", shop.get("id"))


print("\nCARD IDS:")

cards_data = cards_response.json()

for card in cards_data.get("cards", []):
    print("Card ID:", card.get("id"))
    print("Card Number:", card.get("card_number"))