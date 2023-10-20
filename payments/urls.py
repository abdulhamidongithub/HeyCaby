from django.urls import path

from .views import *

urlpatterns = [
    path("", PaymentsAPIView.as_view()),
]
