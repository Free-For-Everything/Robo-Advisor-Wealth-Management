"""Postfix SMTP email client for sending daily reports and alerts via smtplib."""

import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


class PostfixEmailClient:
    """SMTP client using stdlib smtplib to send HTML emails through local Postfix."""

    def __init__(
        self,
        smtp_host: str = "localhost",
        smtp_port: int = 25,
        sender: str = "robo-advisor@local",
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender = sender

    def send_email(
        self,
        to: str | list[str],
        subject: str,
        body_html: str,
        attachments: list[str] | None = None,
    ) -> bool:
        """Send an HTML email with optional file attachments.

        Args:
            to: Recipient address or list of addresses.
            subject: Email subject line.
            body_html: HTML body content.
            attachments: List of file paths to attach.

        Returns:
            True on success, False on any SMTP error.
        """
        recipients = [to] if isinstance(to, str) else list(to)

        msg = MIMEMultipart("mixed")
        msg["From"] = self.sender
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        # HTML body part
        html_part = MIMEText(body_html, "html", "utf-8")
        msg.attach(html_part)

        # Attach files if provided
        if attachments:
            for filepath in attachments:
                path = Path(filepath)
                if not path.is_file():
                    continue
                with open(path, "rb") as fh:
                    part = MIMEApplication(fh.read(), Name=path.name)
                part["Content-Disposition"] = f'attachment; filename="{path.name}"'
                msg.attach(part)

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.sendmail(self.sender, recipients, msg.as_string())
            return True
        except (smtplib.SMTPException, OSError):
            return False

    def send_daily_report(self, to: str | list[str], pdf_path: str) -> bool:
        """Send the daily portfolio report PDF as an email attachment.

        Args:
            to: Recipient address(es).
            pdf_path: Absolute path to the generated PDF report.

        Returns:
            True on success, False on failure.
        """
        filename = Path(pdf_path).name
        subject = f"Daily Portfolio Report — {filename}"
        body_html = (
            "<h2>Daily Portfolio Report</h2>"
            f"<p>Please find today's report attached: <strong>{filename}</strong></p>"
            "<p>This is an automated message from the Robo-Advisor system.</p>"
        )
        return self.send_email(to, subject, body_html, attachments=[pdf_path])
