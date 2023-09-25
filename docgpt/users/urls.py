from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from users import views

urlpatterns = [
    path('<int:id>', views.UserProfileView.as_view(), name='profile'),
    path('', views.UserProfileView.as_view(), name='profile'),
    path('signup/', views.UserManager.as_view(), name='signup'),
    path('login/', views.CustomTokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('update_password/', views.UserUpdatePassword.as_view(),
         name='updatepassword'),
    path('forgot_password/', views.ForgotPassword.as_view()),
    path('reset/', views.ResetPassword.as_view()),
]
