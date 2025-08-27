from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from ..serializers.password import ResetPasswordSerializer
from typing import Dict, Any, cast
from django.contrib.auth import get_user_model
from ..models.reset_token import ResetToken

User = get_user_model()

class ResetPasswordView(APIView):
    def post(self, request, token):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = cast(Dict[str, Any], serializer.validated_data)
            try:
                reset_token = ResetToken.objects.get(token=token)
                if reset_token.is_expired():
                    reset_token.delete()
                    return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
                user = reset_token.user
                user.set_password(validated_data['password'])
                user.save()
                reset_token.delete()
                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            except ResetToken.DoesNotExist:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)