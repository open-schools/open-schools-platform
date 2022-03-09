from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile", null=True)
    phone_regex = RegexValidator(regex=r'^\+?7?\d{9,15}$',
                                 message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, null=True)  # validators should be a list
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return "Profile: " + self.phone_number


class VerificationSession(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name="profile")
    session = models.CharField(max_length=6, null=True)
    creation_date = models.DateTimeField(editable=True, null=True, blank=True)

    def __str__(self):
        return "VerificationCode: " + self.user_profile.phone_number
