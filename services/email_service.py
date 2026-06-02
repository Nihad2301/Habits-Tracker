import os
import resend
from config import settings

resend.api_key = settings.RESEND_API_KEY

def send_verification_email(email: str, token: str):
    """Send verification email to user."""
    try:
        # Create verification link (you'll need to configure your frontend URL)
        verification_link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        params = {
            "from": "Habit Tracker <onboarding@resend.dev>",
            "to": [email],
            "subject": "Verify your email",
            "html": f"""
                <h2>Welcome to Habit Tracker!</h2>
                <p>Please verify your email by clicking the link below:</p>
                <a href="{verification_link}">Verify Email</a>
                <p>This link will expire in 24 hours.</p>
            """
        }
        
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False