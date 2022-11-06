import datetime
import pytz
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework_jwt.utils import jwt_decode_token
from rest_framework import serializers

from open_schools_platform.organization_management.employees.models import EmployeeProfile
from open_schools_platform.parent_management.parents.models import ParentProfile
from open_schools_platform.student_management.students.models import StudentProfile
from open_schools_platform.user_management.users.models import User, FirebaseNotificationToken
from open_schools_platform.user_management.users.services import is_token_alive, verify_token, \
     user_update, get_jwt_token, update_token_session, generate_user_password, set_new_password_for_user
from open_schools_platform.user_management.users.tests.utils import create_test_user, create_test_token


class UserCreateTests(TestCase):
    def test_user_with_not_valid_phone_cannot_be_created(self):
        create_test_user()

        with self.assertRaises(ValidationError):
            create_test_user(phone="+79022552")

        self.assertEqual(1, User.objects.count())
        self.assertEqual(1, EmployeeProfile.objects.count())
        self.assertEqual(1, ParentProfile.objects.count())
        self.assertEqual(1, StudentProfile.objects.count())
        self.assertEqual(1, FirebaseNotificationToken.objects.count())


class IsTokenAliveTests(TestCase):
    def test_token_with_old_date_of_creation_is_not_alive(self):
        token = create_test_token()
        token.created_at = datetime.datetime(2000, 9, 19, 10, 40, 23, 944737, tzinfo=pytz.UTC)
        token.save()
        result = is_token_alive(token)
        self.assertFalse(result)

    def test_token_with_recent_date_of_creation_is_alive(self):
        token = create_test_token()
        token.created_at = datetime.datetime(2023, 9, 19, 10, 40, 23, 944737, tzinfo=pytz.UTC)
        token.save()
        result = is_token_alive(token)
        self.assertTrue(result)


class TokenCreateTests(TestCase):
    def test_user_without_phone_number_cannot_be_created(self):
        self.assertRaises(ValueError, lambda: create_test_token(phone=""))


class UserUpdateTests(TestCase):
    def test_user_with_valid_data_can_be_updated(self):
        user = create_test_user()
        data_for_user_update = {
            "name": "Schwarz"
        }
        user_update(user=user, data=data_for_user_update)
        self.assertEqual(user.name, "Schwarz")
        self.assertEqual(user.parent_profile.name, 'Schwarz')
        self.assertEqual(user.student_profile.name, 'Schwarz')


class VerifyTokenTests(TestCase):
    def test_successfully_token_verify(self):
        token = create_test_token()
        verify_token(token)
        self.assertTrue(token.is_verified)


class GetJwtTokenTests(TestCase):
    def test_successfully_get_jwt_token(self):
        user = create_test_user()
        user_password = "123456"
        jwt_token = get_jwt_token(user.USERNAME_FIELD, str(user.get_username()), user_password, request=None)
        data_from_jwt = jwt_decode_token(jwt_token)
        self.assertEqual(user.phone, data_from_jwt["username"])

    def test_user_does_not_exist(self):
        self.assertRaises(serializers.ValidationError,
                          lambda: get_jwt_token("+79020000000", "+79020000000", "123456", request=None))


class UpdateTokenSessionTests(TestCase):
    def test_successfully_update_token_session(self):
        token = create_test_token()
        update_token_session(token, "111111")
        self.assertEqual("111111", token.session)


class GenerateUserPassword(TestCase):
    def test_successfully_generate_password_for_user(self):
        user = create_test_user()
        new_user_password = generate_user_password()
        self.assertNotEqual(user.password, new_user_password)


class SetNewPasswordForUserTests(TestCase):
    def test_successfully_set_new_password_for_user(self):
        user = create_test_user()
        set_new_password_for_user(user, "654321")
        result = user.check_password("654321")
        self.assertTrue(result)
