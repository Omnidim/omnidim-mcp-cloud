"""Tool output never carries a credential a customer pasted into a URL, header or field.

CASE-2026-001640: a CRM webhook URL carried its key as `?secret=`; other systems put it in
`token=`, `key=`, `sig=` or a `Bearer` header, which reached the model in clear.
"""

import pytest

from app.services.dispatcher import _redact

HEX = "63d70bce6ec892e9028b42252a0731f1"


@pytest.mark.parametrize(
    "name",
    [
        "secret",
        "token",
        "key",
        "api_key",
        "apikey",
        "sig",
        "signature",
        "auth",
        "password",
        "access_token",
    ],
)
def test_secret_query_values_are_masked(name: str) -> None:
    url = f"https://crm.example.com/hook?tenant=acme&{name}={HEX}&x=1"
    assert _redact(url) == f"https://crm.example.com/hook?tenant=acme&{name}=[redacted]&x=1"


def test_bearer_values_are_masked() -> None:
    assert _redact(f"Authorization: Bearer {HEX}") == "Authorization: Bearer [redacted]"
    assert _redact(f"bearer {HEX}") == "bearer [redacted]"


@pytest.mark.parametrize(
    "key",
    [
        "authorization",
        "Authorization",
        "token",
        "signature",
        "webhook_secret",
        "lead_square_access_key",
        "private_key",
    ],
)
def test_secret_keys_are_masked(key: str) -> None:
    assert _redact({key: HEX}) == {key: "[redacted]"}


def test_evidence_is_kept() -> None:
    kept = {
        "id": 11989127,
        "call_sid": "CA" + HEX,
        "to_number": "+15551234567",
        "total_tokens": 4044,
        "monkey": "keyboard",
        "webhook_url": "https://crm.example.com/hook?tenant=acme",
        "text": "the token was rejected",
    }
    assert _redact(kept) == kept
