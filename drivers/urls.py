from django.urls import path

from drivers.views import *

urlpatterns = [
    path('driver_create/', DriverCreateView.as_view()),
    path('driver_profil/', DriverProfilView.as_view()),
    path('driver_login/', DriverLoginView.as_view()),
    path('driver_sms_chackcode/', DriverChackSmsCodeView.as_view()),
]
