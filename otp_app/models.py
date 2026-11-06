
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import secrets


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class OtpToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps"
    )

    otp_code = models.CharField(
        max_length=6,
        default=generate_otp
    )

    otp_created_at = models.DateTimeField(auto_now_add=True)

    otp_expires_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.email
