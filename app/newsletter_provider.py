import os
from typing import Tuple

import requests


BREVO_URL = "https://api.brevo.com/v3/contacts"


def subscribe_email(email: str) -> Tuple[bool, str]:
    api_key = os.getenv("BREVO_API_KEY", "").strip()
    list_id = os.getenv("BREVO_LIST_ID", "").strip()

    if not api_key or not list_id:
        return False, "brevo_not_configured"

    headers = {
        "accept": "application/json",
        "api-key": api_key,
        "content-type": "application/json",
    }
    payload = {
        "email": email,
        "listIds": [int(list_id)],
        "updateEnabled": True,
    }

    resp = requests.post(BREVO_URL, headers=headers, json=payload, timeout=10)
    if resp.status_code in (200, 201, 204):
        return True, "ok"
    return False, f"brevo_error_{resp.status_code}"
