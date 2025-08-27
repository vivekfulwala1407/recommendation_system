from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from ..models.post import Post
from ..serializer.post import PostSerializer
import os
from ..models.post_metadata import PostMetadata
import logging

logger = logging.getLogger(__name__)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("You can only access your own posts")
        return obj
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.image:
            if os.path.isfile(instance.image.path):
                os.remove(instance.image.path)
        try:
            PostMetadata.objects(post_id=instance.id).delete()
            logger.info(f"Deleted metadata for post {instance.id}")
        except Exception as e:
            logger.error(f"Error deleting metadata: {str(e)}")
        instance.delete()
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)