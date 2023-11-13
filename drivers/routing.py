from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'/orders/', consumers.OrdersConsumer.as_asgi()),
    re_path(r'/drivers_locations/', consumers.DriversLocationConsumer.as_asgi()),
    re_path(r'/driver_location/', consumers.DriverLocationConsumer.as_asgi()),
]
