from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from .models import Post
from .serializers import PostSerializer
import os
from django.conf import settings
from .utils import build_personalized_feed
from .utils_vit import save_metadata
from django.http import Http404
from .models_mongo import PostMetadata
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

class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if hasattr(self, '_feed_cache'):
            delattr(self, '_feed_cache')
        feed = build_personalized_feed(user)
        return feed

class InteractView(generics.GenericAPIView):
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        try:
            instance = self.get_object()
            action = request.data.get('action')
            if action not in ['like', 'comment', 'share']:
                return Response({'error': 'Invalid action. Use: like, comment, or share'}, status=status.HTTP_400_BAD_REQUEST)
            user_id = str(request.user.id)
            if user_id not in instance.interactions:
                instance.interactions[user_id] = {}
            user_actions = instance.interactions[user_id]
            
            if action in user_actions and user_actions[action] > 0:
                user_actions[action] -= 1
                if action == 'like':
                    instance.likes = max(0, instance.likes - 1)
                elif action == 'comment':
                    instance.comments = max(0, instance.comments - 1)
                elif action == 'share':
                    instance.shares = max(0, instance.shares - 1) 
                message = f'Post un{action}d'
                logger.info(f"User {request.user.username} un{action}d post {pk}")
            else:
                user_actions[action] = user_actions.get(action, 0) + 1
                if action == 'like':
                    instance.likes += 1
                elif action == 'comment':
                    instance.comments += 1
                elif action == 'share':
                    instance.shares += 1
                message = f'Post {action}d'
                logger.info(f"User {request.user.username} {action}d post {pk}")
                try:
                    metadata = PostMetadata.objects(post_id=instance.id).first()
                    if metadata:
                        if action == 'like':
                            increment = 1
                        elif action == 'comment':
                            increment = 2  
                        elif action == 'share':
                            increment = 3
                        request.user.update_interest(metadata.category, increment=increment)
                        logger.info(f"Updated user {request.user.username} interest in {metadata.category} by +{increment}")
                except Exception as e:
                    logger.error(f"Error updating user interest: {str(e)}")
            instance.save()
            response_data = {
                'message': message,
                'likes': instance.likes,
                'comments': instance.comments,
                'shares': instance.shares,
                'user_action': {action: user_actions.get(action, 0)}
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Http404:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error in InteractView: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

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