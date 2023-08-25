import secrets
import string
import re
from rest_framework import serializers
from datetime import datetime
from django.core import signing
from django.conf import settings
from django.core.mail import send_mail, BadHeaderError


# For generating a random OTP

def generate_otp():
    return ''.join(secrets.choice(string.digits) for _ in range(settings.OTP_LENGTH))


def sent_mail_user(email, otp):

    try:
        send_mail(
            settings.SMTP_MAIL_BACKEND_EMAIL_SUBJECT,
            settings.SMTP_MAIL_BACKEND_EMAIL_MESSAGE + otp,
            settings.SMTP_MAIL_BACKEND_EMAIL_ADDRESS,
            [email],
            fail_silently=False,
        )
        return True
    except BadHeaderError:
        return False


def encrypt_token(email, otp, expire_minutes):
    expiration_time = datetime.now(
    ) + expire_minutes
    data = f"{email},{otp},{expiration_time}"
    token = signing.dumps(data, key=settings.SIGNING_KEY)
    return token


def decrypt_token(token):
    try:
        data = signing.loads(token, key=settings.SIGNING_KEY)
        email, otp, expiration_time = data.split(',')
        return email, otp, expiration_time
    except signing.BadSignature:
        return None, None, None


def is_expired(expiration_time):
    current_time = datetime.now()
    return expiration_time > current_time


def validate_username(value):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", value):
        raise serializers.ValidationError(
            "Username must be a valid email address.")
    return value
