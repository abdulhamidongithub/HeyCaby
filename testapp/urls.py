from django.urls import path
from .views import IsmView

urlpatterns = [
    path('ism_create/', IsmView.as_view(), name='ism_create'),
]