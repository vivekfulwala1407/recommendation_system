from django.urls import path
from .views import PostCreateView, PostListView, PostDetailView, FeedView, InteractView

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/interact/', InteractView.as_view(), name='post_interact'),
    path('feed/', FeedView.as_view(), name='feed'),
]