# common/audit/urls.py
from django.urls import path
from .views import (
    AuditLogsListApi,
    AuditLogDetailApi,
    AuditLogsStatsApi,
    MarketplaceAuditLogsApi,
    ExportAuditLogsApi,
)

urlpatterns = [
    path('audit/logs', AuditLogsListApi.as_view(), name='audit-logs-list'),
    path('audit/logs/<uuid:log_id>', AuditLogDetailApi.as_view(), name='audit-log-detail'),
    path('audit/stats', AuditLogsStatsApi.as_view(), name='audit-stats'),
    path('audit/export', ExportAuditLogsApi.as_view(), name='audit-export'),

    # Специализированные для маркетплейса
    path('marketplace/audit', MarketplaceAuditLogsApi.as_view(), name='marketplace-audit'),
]