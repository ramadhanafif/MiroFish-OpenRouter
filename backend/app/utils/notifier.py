"""
Push notifications via ntfy (https://ntfy.sh or self-hosted).

Disabled unless NTFY_TOPIC is set. Every call is fire-and-forget: a failed
or slow notification must never block or break the pipeline, so sending
happens on a daemon thread and all exceptions are swallowed (logged at
debug level only).
"""

import logging
import threading

import requests

from ..config import Config

logger = logging.getLogger(__name__)


def notify(title: str, message: str, priority: str = "default", tags: str = "") -> None:
    """
    Send a push notification if ntfy is configured, otherwise no-op.

    Args:
        title: Notification title
        message: Notification body
        priority: ntfy priority (min, low, default, high, urgent)
        tags: Comma-separated ntfy tags (emoji shortcodes like "white_check_mark")
    """
    if not Config.NTFY_TOPIC:
        return

    def _send():
        try:
            url = f"{Config.NTFY_URL.rstrip('/')}/{Config.NTFY_TOPIC}"
            headers = {
                "Title": title,
                "Priority": priority,
            }
            if tags:
                headers["Tags"] = tags
            if Config.NTFY_TOKEN:
                headers["Authorization"] = f"Bearer {Config.NTFY_TOKEN}"
            requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=10)
        except Exception as e:
            logger.debug(f"ntfy notification failed: {e}")

    threading.Thread(target=_send, daemon=True).start()
