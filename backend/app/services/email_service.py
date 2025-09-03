import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from typing import Optional

from ..core.config import settings
from ..utils.email_templates import get_verification_email_template, get_password_reset_email_template

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email

    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_body: str, 
        text_body: Optional[str] = None
    ) -> bool:
        """Send email using SMTP."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email

            # Add text part if provided
            if text_body:
                text_part = MIMEText(text_body, "plain")
                message.attach(text_part)

            # Add HTML part
            html_part = MIMEText(html_body, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password,
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_verification_email(self, email: str, token: str) -> None:
        """Send email verification email."""
        verification_url = f"{settings.frontend_url}/auth/verify-email?token={token}"
        
        html_body = get_verification_email_template(verification_url)
        subject = "Verify Your Email Address"
        
        # For now, we'll use a synchronous approach in development
        # In production, this should be queued with Celery or similar
        if settings.environment == "development":
            logger.info(f"DEVELOPMENT: Verification email for {email}")
            logger.info(f"Verification URL: {verification_url}")
        else:
            # In production, queue this for async processing
            import asyncio
            asyncio.create_task(self.send_email(email, subject, html_body))

    def send_password_reset_email(self, email: str, token: str) -> None:
        """Send password reset email."""
        reset_url = f"{settings.frontend_url}/auth/reset-password?token={token}"
        
        html_body = get_password_reset_email_template(reset_url)
        subject = "Reset Your Password"
        
        # For now, we'll use a synchronous approach in development
        if settings.environment == "development":
            logger.info(f"DEVELOPMENT: Password reset email for {email}")
            logger.info(f"Reset URL: {reset_url}")
        else:
            # In production, queue this for async processing
            import asyncio
            asyncio.create_task(self.send_email(email, subject, html_body))