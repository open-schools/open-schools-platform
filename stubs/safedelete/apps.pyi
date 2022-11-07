from django.apps import AppConfig


class SafeDeleteConfig(AppConfig):
    name: str
    verbose_name: str

    def ready(self) -> None: ...
