from __future__ import annotations

import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_alert_email(to_email: str, endpoint_name: str, alert_type: str, message: str) -> bool:
    """Send an alert email. Returns True if sent, False if SMTP is not configured."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP not configured, skipping email to %s", to_email)
        return False

    subject_map = {
        "down": f"🔴 {endpoint_name} is DOWN",
        "latency": f"🟡 High latency on {endpoint_name}",
        "status": f"🟠 Unexpected status from {endpoint_name}",
    }
    subject = subject_map.get(alert_type, f"⚠️ Alert for {endpoint_name}")

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 600px; margin: 0 auto; padding: 32px;">
      <div style="background: #0f1729; border-radius: 12px; padding: 32px; color: #f3eee2;">
        <h1 style="margin: 0 0 8px; font-size: 24px; color: #8bf0cb;">Sentinel</h1>
        <h2 style="margin: 0 0 24px; font-size: 20px; color: #f3eee2;">{subject}</h2>
        <div style="background: rgba(255,255,255,0.06); border-radius: 8px; padding: 16px; margin-bottom: 24px;">
          <p style="margin: 0; color: #b6c2d0; line-height: 1.6;">{message}</p>
        </div>
        <p style="margin: 0; font-size: 13px; color: #666;">
          Sent by Sentinel API Monitoring
        </p>
      </div>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            start_tls=True,
        )
        logger.info("Alert email sent to %s for %s", to_email, endpoint_name)
        return True
    except Exception:
        logger.exception("Failed to send alert email to %s", to_email)
        return False


async def send_test_alert_email(to_email: str) -> bool:
    """Send a test alert email to verify SMTP config."""
    return await send_alert_email(
        to_email=to_email,
        endpoint_name="Test Endpoint",
        alert_type="down",
        message="This is a test alert from Sentinel. If you received this, your email alerts are configured correctly!",
    )
