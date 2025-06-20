from django.urls import path
from .views import (
    DocumentCreateView, DocumentRetrieveView,
    DocumentParentSignView, DocumentsPendingDirectorView,
    DocumentDirectorSignView,
)

urlpatterns = [
    path('/create', DocumentCreateView.as_view(), name='document-create'),
    path('/<uuid:id>', DocumentRetrieveView.as_view(), name='document-detail'),
    path('/<uuid:id>/sign/parent', DocumentParentSignView.as_view(), name='document-sign-parent'),
    path('/pending-director-signature', DocumentsPendingDirectorView.as_view(), name='documents-pending-director'),
    path('/<uuid:id>/sign/director', DocumentDirectorSignView.as_view(), name='document-sign-director'),
]
