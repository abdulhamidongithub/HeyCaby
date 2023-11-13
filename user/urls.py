from django.urls import path, include
from user.views import *

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('driver_token/', CustomUserTokenView.as_view(), name='token_obtain_pair'),
    path('operator_token/', OperatorTokenView.as_view(), name='operator_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('user_login/', CustomUserLoginView.as_view()),
]