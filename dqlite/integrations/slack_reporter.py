"""Slack notification integration."""

from typing import Optional
import json

try:
    import requests
except ImportError:
    requests = None


def send_report(webhook_url: str, result, title: Optional[str] = None):
    """Send validation result to Slack webhook."""
    if requests is None:
        raise ImportError(
            "requests is required for Slack integration. Install with: pip install requests"
        )

    color = "#36a64f" if result.success else "#ff0000"
    status = "PASS" if result.success else "FAIL"

    payload = {
        "attachments": [
            {
                "color": color,
                "title": title or f"Data Quality Check: {status}",
                "text": result.to_markdown(),
                "footer": "dq-lite",
            }
        ]
    }

    requests.post(webhook_url, json=payload)
