from django.http import JsonResponse
from django.db.utils import OperationalError
from django.db import connections

class DatabaseConnectionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            connections['default'].cursor()
            response = self.get_response(request)
            return response
        except OperationalError as e:
            error_message = str(e)
            if 'Can\'t connect to MySQL server' in error_message:
                return JsonResponse({
                    'error': 'MySQL server is not running. Please start the database server.',
                    'details': error_message
                }, status=503)
            elif 'MySQL server has gone away' in error_message:
                return JsonResponse({
                    'error': 'Lost connection to MySQL server.',
                    'details': error_message
                }, status=503)
            else:
                return JsonResponse({
                    'error': 'Database connection error',
                    'details': error_message
                }, status=500)
