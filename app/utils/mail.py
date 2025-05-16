from flask import app, render_template
from flask_mail import Mail, Message

mail = Mail()

def send_reset_email(to_email, reset_link):
    msg = Message("Your Password Reset Link",
                  recipients=[to_email])
    msg.body = f"Click the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, please ignore."
    mail.send(msg)

def send_verification_code(current_app, current_user, email, code):
    msg = Message(
        subject="Your Email Verification Code",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[email]
    )
    msg.body = (
        f"Hi {current_user.first_name},\n\n"
        f"Your verification code is: {code}\n\n"
        "It will expire in 10 minutes.\n\n"
        "If you didn't request this, please ignore."
    )
    mail.send(msg)

def send_share_dashboard_email(current_app, current_user, to_email, share_url):
    """Send an email to share a dashboard with someone."""
    msg = Message(
        subject=f"FuelPrice Dashboard Shared by {current_user.first_name}",
        sender=current_app.config['MAIL_DEFAULT_SENDER'],
        recipients=[to_email]
    )
    msg.html = render_template(
        'email/share_dashboard.html',
        user=current_user,
        share_url=share_url
    )
    mail.send(msg)