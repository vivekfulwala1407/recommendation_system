from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..serializer.post import PostSerializer
from ..utils.feed import build_personalized_feed
import logging

logger = logging.getLogger(__name__)

class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(self, '_feed_cache'):
            delattr(self, '_feed_cache')
        feed = build_personalized_feed(user)
        return feed