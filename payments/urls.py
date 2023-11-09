from django.urls import path

from .views import *
from .payme_views import *
from .click_views import *

urlpatterns = [
    path("", PaymentsAPIView.as_view()),
    path("clickuz/", ClickView.as_view()),
    path("paymeuz/", PaycomView.as_view()),
]
