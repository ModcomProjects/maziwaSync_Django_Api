from django.urls import path
from .views import LogoutView, RegisterView, LoginView, MeView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/register/', RegisterView, name='register'),
    path('auth/login/', LoginView, name='login'),
    path('auth/logout/', LogoutView, name='logout'),
    path('auth/me/', MeView, name='me'),

    # Refresh endpoint
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]