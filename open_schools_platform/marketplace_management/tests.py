from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from open_schools_platform.marketplace_management.models import (
    Installation,
    App,
    DeveloperProfile,
    Category
)
from open_schools_platform.organization_management.organizations.models import Organization
from open_schools_platform.user_management.users.models import User


class InstallationDeleteTests(APITestCase):
    """Тесты для удаления установок"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = APIClient()

        # Создаем пользователя
        self.user = User.objects.create_user(
            phone="+12345678912",
            name="test_user",
            password="testpass123"
        )

        # Создаем DeveloperProfile
        self.developer_profile = DeveloperProfile.objects.create(
            user=self.user,
            email="developer@example.com",
            github="https://github.com/dev"
        )

        # Создаем категорию
        self.category = Category.objects.create(
            name="Test Category"
        )

        # Создаем тестовое приложение
        self.app = App.objects.create(
            name="Test Application",
            description="Test app description",
            type="internal",
            status="published",
            icon_url="http://example.com/icon.png",
            developer_profile=self.developer_profile
        )
        self.app.category.add(self.category)

        # Создаем организацию
        self.organization = Organization.objects.create(
            name="Test Organization",
            inn="1234567890"
        )

        # Создаем установку
        self.installation = Installation.objects.create(
            app=self.app,
            organization=self.organization,
            user=self.user,
            config_data={"settings": {"theme": "dark"}}
        )

        # URL для деталей установки (удаление)
        self.detail_url = f"/api/marketplace-management/marketplace/installations/{self.installation.id}"

    def test_delete_installation_success(self):
        """Тест успешного удаления установки"""
        # Проверяем, что установка существует
        self.assertEqual(Installation.objects.count(), 1)

        # Отправляем DELETE запрос
        response = self.client.delete(self.detail_url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что установка удалена из базы данных
        self.assertEqual(Installation.objects.count(), 0)

        # Проверяем, что объект действительно удален
        with self.assertRaises(Installation.DoesNotExist):
            Installation.objects.get(id=self.installation.id)

    def test_delete_installation_not_found(self):
        """Тест удаления несуществующей установки"""
        # Отправляем DELETE запрос
        response = self.client.delete(self.detail_url)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что установки нет
        self.assertEqual(Installation.objects.count(), 0)

        # Пытаемся удалить уже удаленную установку
        response = self.client.delete(self.detail_url)

        # Проверяем, что получили 404
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
