from flask import app
from flask_mail import Mail, Message

mail = Mail()

def send_reset_email(to_email, reset_link):
    msg = Message("Your Password Reset Link",
                  recipients=[to_email])
    msg.body = f"Click the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, please ignore."
    mail.send(msg)
