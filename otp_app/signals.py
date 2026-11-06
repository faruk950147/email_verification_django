
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
import logging

from .models import OtpToken

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):

    if not created:
        return

    if instance.is_superuser:
        return

    def generate_and_send_otp():

        try:
            # Generate OTP
            otp = OtpToken.objects.create(
                user=instance,
                otp_expires_at=timezone.now() + timedelta(minutes=5)
            )

            # Deactivate user until verification
            sender.objects.filter(pk=instance.pk).update(
                is_active=False
            )

            subject = "Email Verification"

            message = f"""
Hi {instance.username},

Your OTP is: {otp.otp_code}

This OTP will expire in 5 minutes.

Verify your email using the link below:

http://127.0.0.1:8000/verify-email/{instance.username}

Thank you.
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )

        except Exception:
            logger.exception(
                "Failed to generate or send OTP for user %s",
                instance.pk
            )

    transaction.on_commit(generate_and_send_otp)
