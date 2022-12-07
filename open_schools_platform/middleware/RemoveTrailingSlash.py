from django.utils.deprecation import MiddlewareMixin


class RemoveTrailingSlashMiddleware(MiddlewareMixin):
    def process_request(self, request):
        address = request.path_info.split('/')
        if len(address) > 1:
            context = address[1]
            if context == 'api' and request.path_info.endswith('/'):
                request.path_info = request.path_info[:-1]
                request.path = request.path[:-1]
        return self.get_response(request)
