from django.test import TestCase
from open_schools_platform.user_management.users.models import User


class UserCreateTests(TestCase):
    fixtures = ["test_db.json"]

    def setUp(self):
        pass

    def test_something(self):
        self.assertEqual(4, User.objects.count())
