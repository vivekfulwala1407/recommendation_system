from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers.password import ForgotPasswordSerializer
import uuid
from typing import Dict, Any, cast
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models.reset_token import ResetToken

User = get_user_model()

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = cast(Dict[str, Any], serializer.validated_data)
            email = validated_data['email']
            try:
                user = User.objects.get(email=email)
                token = uuid.uuid4()
                expires_at = timezone.now() + timedelta(hours=1)
                ResetToken.objects.create(user=user, token=token, expires_at=expires_at)
                reset_link = f"http://127.0.0.1:8000/auth/reset-password/{token}/"
                return Response({"message": "Reset link generated", "reset_link": reset_link}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({"error": "This email does not exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)