# common/audit/views.py
from drf_yasg import openapi
from drf_yasg.openapi import Parameter, IN_QUERY, TYPE_STRING, FORMAT_DATE, Schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from open_schools_platform.api.mixins import ApiAuthMixin
from open_schools_platform.api.pagination import get_paginated_response
from open_schools_platform.api.swagger_tags import SwaggerTags
from open_schools_platform.common.paginators import DefaultListPagination
from open_schools_platform.common.services import filter_queryset_by_dates
from open_schools_platform.common.views import convert_dict_to_serializer
from .models import AuditLog, AuditEventType
from .selectors import get_audit_logs, get_audit_log
from .serializers import GetAuditLogSerializer, AuditLogFilterSerializer


class AuditLogsListApi(ApiAuthMixin, ListAPIView):
    """
    API для получения списка логов аудита с фильтрацией
    Доступно только администраторам
    """
    queryset = AuditLog.objects.all()
    pagination_class = DefaultListPagination

    @swagger_auto_schema(
        tags=[SwaggerTags.AUDIT],
        operation_description="Получить список логов аудита с фильтрацией. Только для администраторов.",
        manual_parameters=[
            Parameter(
                'event_type',
                IN_QUERY,
                type=TYPE_STRING,
                enum=[choice[0] for choice in AuditEventType.choices],
                description="Тип события"
            ),
            Parameter('user_id', IN_QUERY, type=TYPE_STRING, format='uuid', description="ID пользователя"),
            Parameter('app_id', IN_QUERY, type=TYPE_STRING, format='uuid', description="ID приложения"),
            Parameter('organization_id', IN_QUERY, type=TYPE_STRING, format='uuid', description="ID организации"),
            Parameter('date_from', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE, description="Дата начала"),
            Parameter('date_to', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE, description="Дата окончания"),
            Parameter('search', IN_QUERY, type=TYPE_STRING, description="Поиск по описанию"),
            Parameter('page', IN_QUERY, type='integer', description="Номер страницы"),
            Parameter('page_size', IN_QUERY, type='integer', description="Размер страницы"),
        ],
        responses={
            200: convert_dict_to_serializer({"results": GetAuditLogSerializer(many=True)}),
            403: "Доступ запрещен"
        }
    )
    def get(self, request):
        # Проверка прав - только администраторы
        if not request.user.is_staff:
            return Response(
                {"error": "Доступ разрешен только администраторам"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Валидация фильтров
        filter_serializer = AuditLogFilterSerializer(data=request.GET.dict())
        filter_serializer.is_valid(raise_exception=True)

        # Получаем логи с фильтрацией
        logs = get_audit_logs(filters=filter_serializer.validated_data)

        # Возвращаем пагинированный ответ
        response = get_paginated_response(
            pagination_class=DefaultListPagination,
            serializer_class=GetAuditLogSerializer,
            queryset=logs,
            request=request,
            view=self
        )

        return response


class AuditLogDetailApi(ApiAuthMixin, APIView):
    """
    API для получения детальной информации о логе аудита
    """

    @swagger_auto_schema(
        tags=[SwaggerTags.AUDIT],
        operation_description="Получить детальную информацию о логе аудита по ID. Только для администраторов.",
        responses={
            200: convert_dict_to_serializer({"audit_log": GetAuditLogSerializer()}),
            403: "Доступ запрещен",
            404: "Лог не найден"
        }
    )
    def get(self, request, log_id):
        # Проверка прав
        if not request.user.is_staff:
            return Response(
                {"error": "Доступ разрешен только администраторам"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем лог
        audit_log = get_audit_log(filters={'id': str(log_id)})

        if not audit_log:
            return Response(
                {"error": "Лог аудита не найден"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"audit_log": GetAuditLogSerializer(audit_log).data},
            status=status.HTTP_200_OK
        )


class AuditLogsStatsApi(ApiAuthMixin, APIView):
    """
    API для получения статистики по логам аудита
    """

    @swagger_auto_schema(
        tags=[SwaggerTags.AUDIT],
        operation_description="Получить статистику по логам аудита. Только для администраторов.",
        manual_parameters=[
            Parameter('date_from', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE, description="Дата начала"),
            Parameter('date_to', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE, description="Дата окончания"),
            Parameter('event_type', IN_QUERY, type=TYPE_STRING, description="Тип события для фильтрации"),
        ],
        responses={
            200: Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_count': openapi.Schema(type=openapi.TYPE_INTEGER, description="Общее количество логов"),
                    'by_event_type': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Количество логов по типам событий"
                    ),
                    'by_user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Топ пользователей по активности"
                    ),
                    'by_app': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Топ приложений по событиям"
                    ),
                    'by_organization': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        description="Топ организаций по событиям"
                    ),
                }
            ),
            403: "Доступ запрещен"
        }
    )
    def get(self, request):
        # Проверка прав
        if not request.user.is_staff:
            return Response(
                {"error": "Доступ разрешен только администраторам"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Получаем фильтры
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        event_type = request.GET.get('event_type')

        # Фильтруем логи
        filters = {}
        if event_type:
            filters['event_type'] = event_type

        logs = get_audit_logs(filters=filters)

        # Фильтрация по датам если указаны
        if date_from and date_to:
            logs = filter_queryset_by_dates(logs, date_from, date_to)

        # Статистика по типам событий
        by_event_type = {}
        for choice in AuditEventType.choices:
            count = logs.filter(event_type=choice[0]).count()
            if count > 0:
                by_event_type[choice[1]] = count  # Используем human-readable название

        # Топ пользователей
        from django.db.models import Count
        by_user = logs.filter(user__isnull=False).values(
            'user__id', 'user__username', 'user__email'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Топ приложений
        by_app = logs.filter(app__isnull=False).values(
            'app__id', 'app__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Топ организаций
        by_organization = logs.filter(organization__isnull=False).values(
            'organization__id', 'organization__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]

        # Формируем ответ
        stats = {
            'total_count': logs.count(),
            'by_event_type': by_event_type,
            'by_user': list(by_user),
            'by_app': list(by_app),
            'by_organization': list(by_organization),
        }

        return Response(stats, status=status.HTTP_200_OK)


class MarketplaceAuditLogsApi(ApiAuthMixin, ListAPIView):
    """
    API для получения логов аудита маркетплейса
    Специализированный endpoint для событий маркетплейса
    """
    queryset = AuditLog.objects.all()
    pagination_class = DefaultListPagination

    @swagger_auto_schema(
        tags=[SwaggerTags.MARKETPLACE_MANAGEMENT],
        operation_description="Получить логи аудита для маркетплейса с фильтрацией по событиям.",
        manual_parameters=[
            Parameter(
                'event_type',
                IN_QUERY,
                type=TYPE_STRING,
                enum=[
                    'app_installation',
                    'app_uninstallation',
                    'app_moderation',
                    'app_update',
                    'policy_change'
                ],
                description="Тип события маркетплейса"
            ),
            Parameter('app_id', IN_QUERY, type=TYPE_STRING, format='uuid', description="ID приложения"),
            Parameter('organization_id', IN_QUERY, type=TYPE_STRING, format='uuid', description="ID организации"),
            Parameter('date_from', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE),
            Parameter('date_to', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE),
        ],
        responses={
            200: convert_dict_to_serializer({"results": GetAuditLogSerializer(many=True)}),
            403: "Доступ запрещен"
        }
    )
    def get(self, request):
        # Проверка прав - можно расширить для разных ролей
        if not request.user.is_staff and not request.user.has_perm('audit.view_auditlog'):
            return Response(
                {"error": "Доступ запрещен"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Фильтры для маркетплейса
        filters = request.GET.dict()

        # Ограничиваем только событиями маркетплейса
        marketplace_events = [
            'app_installation',
            'app_uninstallation',
            'app_moderation',
            'app_update',
            'policy_change'
        ]

        if 'event_type' in filters and filters['event_type'] not in marketplace_events:
            raise ValidationError({"event_type": "Недопустимый тип события для маркетплейса"})

        # Добавляем фильтр по событиям маркетплейса если не указан конкретный
        if 'event_type' not in filters:
            filters['event_type__in'] = ','.join(marketplace_events)

        # Получаем логи
        logs = get_audit_logs(filters=filters)

        response = get_paginated_response(
            pagination_class=DefaultListPagination,
            serializer_class=GetAuditLogSerializer,
            queryset=logs,
            request=request,
            view=self
        )

        return response


class ExportAuditLogsApi(ApiAuthMixin, APIView):
    """
    API для экспорта логов аудита в формате CSV/JSON
    """

    @swagger_auto_schema(
        tags=[SwaggerTags.AUDIT],
        operation_description="Экспорт логов аудита. Только для администраторов.",
        manual_parameters=[
            Parameter('format', IN_QUERY, type=TYPE_STRING, enum=['csv', 'json'], default='json'),
            Parameter('date_from', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE),
            Parameter('date_to', IN_QUERY, type=TYPE_STRING, format=FORMAT_DATE),
            Parameter('event_type', IN_QUERY, type=TYPE_STRING),
        ],
        responses={
            200: openapi.Response('Файл с логами', schema=openapi.Schema(type=openapi.TYPE_FILE)),
            403: "Доступ запрещен"
        }
    )
    def get(self, request):
        # Проверка прав
        if not request.user.is_staff:
            return Response(
                {"error": "Доступ разрешен только администраторам"},
                status=status.HTTP_403_FORBIDDEN
            )

        import json
        from django.http import HttpResponse

        # Получаем параметры
        export_format = request.GET.get('format', 'json')
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        event_type = request.GET.get('event_type')

        # Фильтруем логи
        filters = {}
        if event_type:
            filters['event_type'] = event_type

        logs = get_audit_logs(filters=filters)

        if date_from and date_to:
            logs = filter_queryset_by_dates(logs, date_from, date_to)

        # Подготавливаем данные
        data = []
        for log in logs:
            data.append({
                'id': str(log.id),
                'event_type': log.event_type,
                'event_type_display': log.get_event_type_display(),
                'user': log.user.username if log.user else None,
                'user_id': str(log.user.id) if log.user else None,
                'app': log.app.name if log.app else None,
                'app_id': str(log.app.id) if log.app else None,
                'organization': log.organization.name if log.organization else None,
                'organization_id': str(log.organization.id) if log.organization else None,
                'description': log.description,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat(),
            })

        # Формируем ответ в зависимости от формата
        if export_format == 'csv':
            import io
            import csv

            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
            writer.writeheader()
            writer.writerows(data)

            response = HttpResponse(output.getvalue(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'

        else:  # json
            response = HttpResponse(
                json.dumps(data, ensure_ascii=False, indent=2),
                content_type='application/json'
            )
            response['Content-Disposition'] = 'attachment; filename="audit_logs.json"'

        return response
