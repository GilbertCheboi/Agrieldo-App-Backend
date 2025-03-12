from django.urls import path
from .views import UserRegistrationView, CustomTokenObtainPairView,  update_fcm_token, PasswordResetRequestView, PasswordResetView, UserListView  
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('users/', UserRegistrationView.as_view(), name='user-list-create'),  # User registration endpoint
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # Use your custom token view
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Token refresh endpoint
    path('update-fcm-token/', update_fcm_token, name='update_fcm_token'),  # Define the URL pattern
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/confirm/', PasswordResetView.as_view(), name='password-reset-confirm'),
    path("list_users/", UserListView.as_view(), name="user-list"),  # Ensure this line exists


]
