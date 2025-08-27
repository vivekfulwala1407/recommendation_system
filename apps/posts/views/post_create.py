from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models.post import Post
from ..serializer.post import PostSerializer
from django.conf import settings
from ..utils.image_tagging import save_metadata
import logging

logger = logging.getLogger(__name__)

class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            post = serializer.instance
            data = serializer.data
            if data.get('image'):
                image_path = post.image.path
                metadata = save_metadata(post, image_path)
                data['tags'] = metadata['tags']
                data['category'] = metadata['category']
                if isinstance(data['image'], str) and data['image'].startswith(settings.MEDIA_URL):
                    data['image'] = request.build_absolute_uri(data['image'])
                else:
                    data['image'] = request.build_absolute_uri(settings.MEDIA_URL + data['image'])
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)