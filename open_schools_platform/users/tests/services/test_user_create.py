from django.test import TestCase
from django.core.exceptions import ValidationError

from open_schools_platform.users.services import create_user
from open_schools_platform.users.models import User


class UserCreateTests(TestCase):
    def test_user_with_capitalized_email_cannot_be_created(self):
        create_user(
            phone="+79112112943",
            name="Ivan",
            password="qwe",
        )

        with self.assertRaises(ValidationError):
            create_user(
                phone="+791121129",
                name="Ivan",
                password="qwe",
            )

        self.assertEqual(1, User.objects.count())
