from django.urls import path

from .apis import TriggerApiException


urlpatterns = [
    path("exceptions", TriggerApiException.as_view())
]
