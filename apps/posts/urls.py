from django.urls import path
from .views.feed import FeedView
from .views.post_create import PostCreateView
from .views.post_list import PostListView
from .views.post_detail import PostDetailView
from .views.interact import InteractView

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<int:pk>/interact/', InteractView.as_view(), name='post_interact'),
    path('feed/', FeedView.as_view(), name='feed'),
]