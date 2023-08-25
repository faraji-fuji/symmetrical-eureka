from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import datetime
import random

class MyUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_visitor = models.BooleanField(default=False)
    is_checked_in = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True)  # Change to CharField
    otp_expiry = models.DateTimeField(null=True)

    def has_otp_expired(self):
        return self.otp_expiry <= timezone.now()

    def mark_phone_as_verified(self):
        self.is_phone_verified = True
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.otp = str(random.randint(100000, 999999))
            self.otp_expiry = timezone.now() + datetime.timedelta(minutes=3)
        super(MyUser, self).save(*args, **kwargs)


class Building(models.Model):
    bulding_name = models.CharField(max_length=255)


class Floor(models.Model):
    building_id = models.CharField(max_length=255)
    floor_number = models.CharField(max_length=255)


class Office(models.Model):
    floor_id = models.CharField(max_length=255)
    office_name = models.CharField(max_length=255)