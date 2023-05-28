from django.urls import path
from .views import delete_auditor, change_password, get_auditor_id_by_user_id
from .api import RegisterApi, InfoTokenObtainPairView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path("register/", RegisterApi.as_view()),
    path("token/", InfoTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("delete-auditor/<str:id_auditor>", delete_auditor, name="delete_auditor"),
    path(
        "get-auditor-by-user-id/<str:user_id>",
        get_auditor_id_by_user_id,
        name="get_auditor_by_user_id",
    ),
    path("change-password/", change_password, name="change_password"),
]
