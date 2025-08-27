from rest_framework import generics, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..serializers.register import RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': 'Account created successfully'}, status=status.HTTP_201_CREATED)