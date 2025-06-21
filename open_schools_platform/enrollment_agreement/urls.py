from django.urls import path
from .views import (
    DocumentCreateView, DocumentRetrieveView,
    DocumentParentSignView, DocumentsPendingDirectorView,
    DocumentDirectorSignView, DocumentsByParentView,
)

urlpatterns = [
    path('/create', DocumentCreateView.as_view(), name='document-create'),
    path('/<uuid:id>', DocumentRetrieveView.as_view(), name='document-detail'),
    path('/<uuid:id>/sign/parent', DocumentParentSignView.as_view(), name='document-sign-parent'),
    path('/pending-director-signature', DocumentsPendingDirectorView.as_view(), name='documents-pending-director'),
    path('/<uuid:id>/sign/director', DocumentDirectorSignView.as_view(), name='document-sign-director'),
    path('/by-parent/<uuid:parent_id>', DocumentsByParentView.as_view(), name='document-sign-director'),
]
