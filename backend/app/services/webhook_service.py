"""Webhook service for SIH integration events.

Emits webhook events for:
- low_stock: Critical stock level for a blood type
- expiring_blood: Blood bags nearing expiry date
- transfusion_reaction: Adverse transfusion reaction reported
"""

import hashlib
import hmac
import json
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config.settings import settings


class WebhookEvent:
    """Webhook event structure for SIH integration."""

    LOW_STOCK = "low_stock"
    EXPIRING_BLOOD = "expiring_blood"
    TRANSFUSION_REACTION = "transfusion_reaction"

    def __init__(
        self,
        event_type: str,
        data: dict,
        timestamp: Optional[datetime] = None,
    ):
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "event": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "source": "bloodtrace",
            "data": self.data,
        }


def _sign_payload(payload: str) -> str:
    """Create HMAC-SHA256 signature for webhook payload verification."""
    return hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256,
    ).hexdigest()


async def emit_webhook(event: WebhookEvent) -> list[dict]:
    """Send a webhook event to all configured URLs.

    Returns a list of delivery results.
    """
    if not settings.WEBHOOK_URLS:
        return []

    payload = json.dumps(event.to_dict(), default=str)
    signature = _sign_payload(payload)

    headers = {
        "Content-Type": "application/json",
        "X-BloodTrace-Event": event.event_type,
        "X-BloodTrace-Signature": f"sha256={signature}",
    }

    results = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for url in settings.WEBHOOK_URLS:
            try:
                response = await client.post(url, content=payload, headers=headers)
                results.append({
                    "url": url,
                    "status": response.status_code,
                    "success": response.is_success,
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "status": None,
                    "success": False,
                    "error": str(e),
                })

    return results


async def emit_low_stock_alert(
    blood_group: str, available_count: int, threshold: int
) -> list[dict]:
    """Emit a low stock alert webhook."""
    event = WebhookEvent(
        event_type=WebhookEvent.LOW_STOCK,
        data={
            "blood_group": blood_group,
            "available_count": available_count,
            "threshold": threshold,
            "severity": "critical" if available_count == 0 else "warning",
        },
    )
    return await emit_webhook(event)


async def emit_expiring_blood_alert(
    blood_bag_id: int, blood_group: str, expiry_date: str, days_remaining: int
) -> list[dict]:
    """Emit an expiring blood alert webhook."""
    event = WebhookEvent(
        event_type=WebhookEvent.EXPIRING_BLOOD,
        data={
            "blood_bag_id": blood_bag_id,
            "blood_group": blood_group,
            "expiry_date": expiry_date,
            "days_remaining": days_remaining,
        },
    )
    return await emit_webhook(event)


async def emit_transfusion_reaction_alert(
    transfusion_id: int,
    patient_ipp: str,
    reaction_type: str,
    reaction_details: Optional[str] = None,
) -> list[dict]:
    """Emit a transfusion reaction alert webhook."""
    event = WebhookEvent(
        event_type=WebhookEvent.TRANSFUSION_REACTION,
        data={
            "transfusion_id": transfusion_id,
            "patient_ipp": patient_ipp,
            "reaction_type": reaction_type,
            "reaction_details": reaction_details,
            "severity": "critical" if reaction_type == "severe" else "warning",
        },
    )
    return await emit_webhook(event)
