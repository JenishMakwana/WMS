import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


async def send_reset_password_email(email: str, token: str) -> None:
    # Ensure no double slashes in URL
    base_url = str(settings.FRONTEND_URL).rstrip("/")
    reset_url = f"{base_url}/auth/reset-password?token={token}"

    message = MIMEMultipart("alternative")
    message["Subject"] = "CoreInventory — Reset your password"
    
    from_email = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
    if not from_email:
        print("[CoreInventory Error] EMAILS_FROM_EMAIL and SMTP_USER are both empty! Email will fail.")
        return

    message["From"] = f"{settings.EMAILS_FROM_NAME} <{from_email}>"
    message["To"] = email

    html_body = f"""
    <html>
      <body style="font-family: sans-serif; padding: 32px; color: #1a1a1a;">
        <h2>Reset your CoreInventory password</h2>
        <p>Click the button below to reset your password. This link expires in <strong>1 hour</strong>.</p>
        <a href="{reset_url}"
           style="display:inline-block;padding:12px 24px;background:#534AB7;color:#fff;
                  border-radius:8px;text-decoration:none;font-weight:500;">
          Reset password
        </a>
        <p style="margin-top:24px;color:#888;font-size:13px;">
          If you didn't request this, you can safely ignore this email.
        </p>
      </body>
    </html>
    """

    message.attach(MIMEText(html_body, "html"))

    # In development, only skip if the password is empty. 
    # If a password is provided, we attempt to send.
    if settings.APP_ENV == "development" and not settings.SMTP_PASSWORD:
        print("\n" + "="*50)
        print("[Development] EMAIL PREVIEW (No SMTP Password set)")
        print(f"To: {email}")
        print(f"Reset URL: {reset_url}")
        print("="*50 + "\n")
        return

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
    except Exception as e:
        print(f"[CoreInventory Error] Failed to send email via SMTP: {e}")
        if settings.APP_ENV == "development":
            print("\n" + "!"*50)
            print("[Development Fallback] SMTP Failed, here is the reset URL:")
            print(f"Reset URL: {reset_url}")
            print("!"*50 + "\n")
        else:
            raise e
