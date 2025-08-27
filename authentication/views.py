from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
import uuid
from typing import Dict, Any, cast

User = get_user_model()

reset_token: Dict[str, int] = {}

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)

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

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = cast(Dict[str, Any], serializer.validated_data)
            email = validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = str(uuid.uuid4())
                reset_token[token] = user.pk
                reset_link = f"http://domain/auth/reset-password/{token}/"
                return Response({"message": "Reset link generated", "reset_link": reset_link}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "This email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    def post(self, request, token):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = cast(Dict[str, Any], serializer.validated_data)
            if token in reset_token:
                user_id = reset_token.pop(token)
                try:
                    user = User.objects.get(pk=user_id)
                    user.set_password(validated_data['password'])
                    user.save()
                    return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
                except User.DoesNotExist:
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)