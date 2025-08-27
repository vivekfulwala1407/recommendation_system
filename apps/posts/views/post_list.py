from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models.post import Post
from ..serializer.post import PostSerializer
import logging

logger = logging.getLogger(__name__)

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]