from django.utils.deprecation import MiddlewareMixin

from open_schools_platform.user_management.users.models import User


class LastLoginIPMiddleware(MiddlewareMixin):
    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            user = User.objects.get(id=request.user.id)
            current_ip = LastLoginIPMiddleware._get_ip(request=request)
            if current_ip != user.last_login_ip_address:
                user.last_login_ip_address = current_ip
                user.save()
        return response

    @staticmethod
    def _get_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
