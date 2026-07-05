import resend
from config import settings
from exceptions import EmailDeliveryError

resend.api_key = settings.RESEND_API_KEY

def send_email(email: str, token: str, email_type: str):
    """Send email to user."""
    if email_type == "email_verification":
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        subject = "Verify your email"
        message = f"""
            <h2>Welcome to Habit Tracker!</h2>
            <p>Please verify your email by clicking the link below:</p>
            <a href="{verification_link}">Verify Email</a>
            <p>This link will expire in 24 hours.</p>
        """
    elif email_type == "password_reset":
        password_reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        subject = "Reset your password"
        message = f"""
            <h2>Reset your password</h2>
            <p>Please reset your password by clicking the link below:</p>
            <a href="{password_reset_link}">Reset Password</a>
            <p>This link will expire in 24 hours.</p>
        """
    else:
        raise ValueError(f"Invalid email type: {email_type}")

    try:
        params = {
            "from": "Habit Tracker <onboarding@resend.dev>",
            "to": [email],
            "subject": subject,
            "html": message
        }
        
        resend.Emails.send(params)
    except Exception:
        raise EmailDeliveryError()
        
