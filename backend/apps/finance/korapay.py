import hashlib
import hmac
import requests
import time
import secrets
from decimal import Decimal
from django.conf import settings


class KoraPayService:
    def __init__(self):
        self.public_key = getattr(settings, 'KORA_PAY_PUBLIC_KEY', '')
        self.secret_key = getattr(settings, 'KORA_PAY_SECRET_KEY', '')
        self.webhook_secret = getattr(settings, 'KORA_PAY_WEBHOOK_SECRET', '')
        self.api_url = getattr(settings, 'KORA_PAY_API_URL', 'https://api.korapay.com/merchant/api/v1')

    def generate_reference(self):
        timestamp = int(time.time())
        random_part = secrets.token_hex(8)
        return f"EDIV-{timestamp}-{random_part}"

    def initialize_payment(self, amount, reference, customer_name, customer_email,
                           metadata=None, notification_url=None):
        amount_kobo = int(Decimal(str(amount)) * 100)

        payload = {
            'key': self.public_key,
            'reference': reference,
            'amount': amount_kobo,
            'currency': 'NGN',
            'customer': {
                'name': customer_name,
                'email': customer_email,
            },
            'metadata': metadata or {},
            'channels': ['card', 'bank_transfer', 'bank', 'ussd'],
        }
        if notification_url:
            payload['notification_url'] = notification_url

        return {
            'public_key': self.public_key,
            'reference': reference,
            'amount': amount_kobo,
            'currency': 'NGN',
            'customer_name': customer_name,
            'customer_email': customer_email,
            'notification_url': notification_url,
        }

    def verify_webhook_signature(self, payload_body, signature_header):
        """Verify webhook signature. Raises ValueError if webhook secret not configured."""
        if not self.webhook_secret:
            raise ValueError('KORA_PAY_WEBHOOK_SECRET not configured - webhook verification disabled')
        if not signature_header:
            return False

        expected = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload_body,
            hashlib.sha512,
        ).hexdigest()

        return hmac.compare_digest(expected, signature_header)

    def verify_transaction(self, reference):
        url = f"{self.api_url}/transactions/{reference}"
        headers = {
            'Authorization': f"Bearer {self.secret_key}",
            'Content-Type': 'application/json',
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
