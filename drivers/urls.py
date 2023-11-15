from django.urls import path

from drivers.views import *

urlpatterns = [
    path('finish_order/', DriverFinishedOrder.as_view()),
    path('start_order/', DriverStartOrder.as_view()),
    path('accept_order/', DriverAccaptOrder.as_view()),
    path('location/', DriverLocationPost.as_view()),
    path('profil/', DriverProfilView.as_view()),
    path('login/', DriverLoginView.as_view()),
    path('sms_chackcode/', DriverChackSmsCodeView.as_view()),
]
