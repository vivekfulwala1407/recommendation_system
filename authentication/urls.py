from django.urls import path
from .views import RegisterView, LoginView, ForgotPasswordView, ResetPasswordView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('signup/', RegisterView.as_view(), name='signup'),
    path('signin/', LoginView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
]