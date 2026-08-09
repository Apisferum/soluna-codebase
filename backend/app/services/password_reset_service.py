import smtplib
import ssl
from email.message import EmailMessage

from app.core.config import settings


RESET_REQUEST_MESSAGE = (
    "If an account exists for that email, a reset code has been sent. "
    "Please also check the spam folder."
)


def send_password_reset_email(
    to_email: str,
    code: str,
) -> None:
    from_email = settings.email_from_address

    if (
        not settings.smtp_username
        or not settings.smtp_password
        or not from_email
    ):
        raise RuntimeError(
            "SMTP settings are missing. Check SMTP_USERNAME, "
            "SMTP_PASSWORD, and SMTP_FROM_EMAIL in backend/.env."
        )

    message = EmailMessage()
    message["Subject"] = (
        "Your Synestra AI password reset code"
    )
    message["From"] = from_email
    message["To"] = to_email

    message.set_content(
        f"""Hello,

Your Synestra AI password reset code is:

{code}

This code expires in {settings.reset_code_expire_minutes} minutes
and can be used only once.

If you did not request this password reset, you can ignore this email.

Synestra AI
"""
    )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(
        settings.smtp_host,
        settings.smtp_port,
        context=context,
        timeout=20,
    ) as smtp:
        smtp.login(
            settings.smtp_username,
            settings.smtp_password,
        )
        smtp.send_message(message)