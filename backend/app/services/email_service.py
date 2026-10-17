import smtplib
import uuid
from email.message import EmailMessage

from app.core.config import settings


class EmailDeliveryError(Exception):
    pass


def render_invitation(job_title: str, candidate_name: str | None, recruiter_name: str, recruiter_contact: str | None) -> tuple[str, str]:
    greeting = f"Hello {candidate_name}," if candidate_name else "Hello,"
    contact = f"If you have questions, contact {recruiter_contact}." if recruiter_contact else "Please reply to this email if you have questions."
    return f"Next steps regarding {job_title}", f"""{greeting}

Thank you for your interest in the {job_title} opportunity. Based on an initial resume screening, we would like to invite you to continue to the next step.

Please follow the next-step instructions shared by the recruiting team or reply to this message to confirm your interest. This message does not book an interview time.

{contact}

Best regards,
{recruiter_name}
"""


def send_invitation(*, recipient: str, job_title: str, candidate_name: str | None, recruiter_name: str, recruiter_contact: str | None) -> str:
    if settings.EMAIL_PROVIDER != "smtp" or not settings.SMTP_HOST or not settings.EMAIL_FROM:
        raise EmailDeliveryError("Email provider is not configured")
    subject, body = render_invitation(job_title, candidate_name, recruiter_name, recruiter_contact)
    message = EmailMessage()
    message["From"] = settings.EMAIL_FROM
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USERNAME:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD or "")
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryError("Email provider rejected the message") from exc
    return str(uuid.uuid4())
