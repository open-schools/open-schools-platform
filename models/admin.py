from django.contrib import admin

from models.models import UserProfile, VerificationSession

admin.site.register(UserProfile)
admin.site.register(VerificationSession)
