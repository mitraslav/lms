import requests
from django.conf import settings
from rest_framework.serializers import ValidationError

STRIPE_API_BASE = "https://api.stripe.com/v1"


def _stripe_request(method: str, path: str, data: dict | None = None) -> dict:
    if not settings.STRIPE_SECRET_KEY:
        raise ValidationError("STRIPE_SECRET_KEY is not configured.")

    resp = requests.request(
        method=method,
        url=f"{STRIPE_API_BASE}{path}",
        data=data or {},
        auth=(settings.STRIPE_SECRET_KEY, ""),  # Basic Auth
        timeout=20,
    )

    payload = resp.json()
    if resp.status_code >= 400:
        raise ValidationError({"stripe_error": payload.get("error", payload)})

    return payload


def create_product(name: str, description: str | None = None) -> dict:
    data = {"name": name}
    if description:
        data["description"] = description
    return _stripe_request("POST", "/products", data=data)


def create_price(product_id: str, amount: float, currency: str) -> dict:
    # amount в рублях → в копейках
    unit_amount = int(round(float(amount) * 100))

    data = {
        "unit_amount": unit_amount,
        "currency": currency,
        "product": product_id,
    }
    return _stripe_request("POST", "/prices", data=data)


def create_checkout_session(price_id: str) -> dict:
    data = {
        "mode": "payment",
        "success_url": settings.STRIPE_SUCCESS_URL,
        "cancel_url": settings.STRIPE_CANCEL_URL,

        # form-encoding для line_items
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": 1,
    }
    return _stripe_request("POST", "/checkout/sessions", data=data)


def retrieve_checkout_session(session_id: str) -> dict:
    return _stripe_request("GET", f"/checkout/sessions/{session_id}")
