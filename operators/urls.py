from django.urls import path

from operators.views import *

urlpatterns = [
    path('order_create/', OrderCreate.as_view()),
    path('driver_create/', DriverCreateView.as_view()),
    path('driver_get/', OperatorDriverDetailView.as_view()),
    path('car_categories_get/', CarCategoriesView.as_view()),
    path('orders_get/', OrdersView.as_view()),
    path('operator_get/', OperatorGet.as_view(), name='operator_get'),
    path('drivers_get_operator/', DriversGetOperator.as_view(), name='operator_get'),
    path('order_delete/', OrderDelete.as_view()),
    path('driver_delete/', DriverDelete.as_view()),
]
