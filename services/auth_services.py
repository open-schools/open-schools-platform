from auth_manager.utils.otp import OTPFromPhoneNumber
from models.models import UserProfile, VerificationSession


def create_unverified_user_profile(phone_number):
    return UserProfile.objects.create(phone_number=phone_number)


def get_userprofile_by_phone_number(phone_number):
    return UserProfile.objects.filter(
        phone_number=phone_number
    )


def create_verification_session(user_profile, session):
    otp = OTPFromPhoneNumber(user_profile.phone_number)

    return VerificationSession.objects.create(
        user_profile=user_profile,
        verification_session=session,
        verification_session_creation_date=otp.get_otp_creation_date(),
    )


def edit_verification_session(user_profile, session):
    otp = VerificationSession.objects.filter(
        user_profile=user_profile
    ).get()

    otp_object = OTPFromPhoneNumber(user_profile.phone_number)

    otp.verification_session = session
    otp.verification_session_creation_date = otp_object.otp_creation_date
    otp.save()

    return otp
