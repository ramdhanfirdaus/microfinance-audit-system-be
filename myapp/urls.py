from django.urls import path

from .views import home_admin

urlpatterns = [
    path('', home_admin, name='home_admin'),
]
