# common/audit/middleware.py
from threading import local

_thread_locals = local()


def get_current_user():
    """Получение текущего пользователя"""
    return getattr(_thread_locals, 'user', None)


def get_current_request():
    """Получение текущего запроса"""
    return getattr(_thread_locals, 'request', None)


class AuditMiddleware:
    """Middleware для сохранения пользователя и запроса"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Сохраняем пользователя и запрос в thread local
        _thread_locals.user = request.user if request.user.is_authenticated else None
        _thread_locals.request = request

        response = self.get_response(request)

        # Очищаем
        if hasattr(_thread_locals, 'user'):
            delattr(_thread_locals, 'user')
        if hasattr(_thread_locals, 'request'):
            delattr(_thread_locals, 'request')

        return response