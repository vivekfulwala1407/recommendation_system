from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from ..serializers.token import CustomTokenObtainPairSerializer

class LoginView(APIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            data = {
                'message': 'Login successful',
                'access': serializer.validated_data.get('access') # type: ignore
            }
            return Response(data, status=status.HTTP_200_OK)
        else:
            username = request.data.get('username')
            password = request.data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is None:
                return Response({'error': 'Username or password not found'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'error': 'Username or password not found'}, status=status.HTTP_401_UNAUTHORIZED)
