from django.conf.urls import url
from django.urls import path, include
from .api import RegisterApi
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('register/', RegisterApi.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('hasloggedin/', check_has_logged_in, name='has_logged_in'),
    path('hasloggedin/data', get_logged_in_user_data, name='has_logged_in')
]
