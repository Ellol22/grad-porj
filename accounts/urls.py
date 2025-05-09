from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api_sign_up, api_log_in , activate_user


urlpatterns = [
    path('signup/', api_sign_up, name='api_sign_up'),
    path('login/', api_log_in, name='api_log_in'),
    path('activate/<uidb64>/<token>/', activate_user, name='activate_user')
]
