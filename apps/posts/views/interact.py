from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from ..models.post import Post
from django.http import Http404
from ..models.post_metadata import PostMetadata
import logging

logger = logging.getLogger(__name__)
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