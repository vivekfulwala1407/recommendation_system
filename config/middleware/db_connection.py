from django.http import JsonResponse
from django.db.utils import OperationalError

class DatabaseConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
        except OperationalError as e:
            if 'Can\'t connect to MySQL server' in str(e) or 'MySQL server has gone away' in str(e):
                return JsonResponse({'error': 'Database not connected'}, status=500)
            raise 
        return response