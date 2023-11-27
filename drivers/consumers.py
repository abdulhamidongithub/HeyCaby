from rest_framework_simplejwt.tokens import AccessToken

from drivers.models import Drivers
from operators.models import Order, Operators
from operators.serializers import OrderCreateSerializer
from user.models import CustomUser
from .serializers import *
from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *

from math import radians, sin, cos, sqrt, atan2


def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Yer radiusi (km)
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


class OrdersConsumer(AsyncWebsocketConsumer):
    connected_order_consumers = set()

    async def connect(self):
        token = self.scope.get("query_string").decode("utf-8")
        if token.startswith("token="):
            token = token.replace("token=", "")
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.scope["user_id"] = user_id
            except Exception as e:
                await self.close()

        await self.accept()
        OrdersConsumer.connected_order_consumers.add(self)
        await self.channel_layer.group_add("order_group", self.channel_name)
        await self.send_initial_order_list()

    async def disconnect(self, close_code):
        OrdersConsumer.connected_order_consumers.remove(self)
        await self.channel_layer.group_discard("order_group", self.channel_name)

    async def send_initial_order_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        category_id = await self.get_user_category_id(user_id)
        location = await self.get_driver_location(user_id)
        if user.role == "driver":
            order_list = await self.get_order_list(category_id, location)
            await self.send(text_data=json.dumps(order_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga drivers ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_order(self, event):
        await self.send_initial_order_list()

    @sync_to_async
    def get_order_list(self, category_id, location):
        orders = []
        if category_id == 2:
            order_objects = Order.objects.filter(order_status='active').all().order_by('-id')
            serializer = OrderCreateSerializer(order_objects, many=True)
        else:
            order_objects = Order.objects.filter(order_status='active', is_comfort=False).all().order_by('-id')
            serializer = OrderCreateSerializer(order_objects, many=True)
        for order in serializer.data:

            if calculate_distance(float(location.latitude), float(location.longitude),
                                  float(order['starting_point_lat']), float(order['starting_point_long'])) <= 3:
                orders.append(order)
        return orders

    @sync_to_async
    def get_user_by_id(self, user_id):
        driver = Drivers.objects.filter(id=user_id).first()
        return driver

    @sync_to_async
    def get_user_category_id(self, user_id):
        driver = Drivers.objects.filter(id=user_id).first()
        return driver.category.id

    @sync_to_async
    def get_driver_location(self, user_id):
        location = DriverLocation.objects.filter(driver__id=user_id).first()
        return location


class DriversLocationConsumer(AsyncWebsocketConsumer):
    """
    Operator uchun hamma driverlar
    """

    async def connect(self):
        token = self.scope.get("query_string").decode("utf-8")
        if token.startswith("token="):
            token = token.replace("token=", "")
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.scope["user_id"] = user_id
            except Exception as e:
                await self.close()

        await self.accept()
        await self.channel_layer.group_add("driver_location_group", self.channel_name)
        await self.send_initial_driver_loc_list()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("driver_location_group", self.channel_name)

    async def send_initial_driver_loc_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        if user.role == "operator":
            drivers_list = await self.get_locations_list()
            await self.send(text_data=json.dumps(drivers_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga drivers location ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_driver_location(self, event):
        await self.send_initial_driver_loc_list()

    @sync_to_async
    def get_locations_list(self):
        loc_objects = DriverLocation.objects.all().order_by('-id')
        serializer = DriverLocationSerializer(loc_objects, many=True)
        return serializer.data

    @sync_to_async
    def get_user_by_id(self, user_id):
        return Operators.objects.filter(id=user_id).first()


class DriverLocationConsumer(AsyncWebsocketConsumer):
    """
    Operator uchun bita driver, token=operator token, driver_id = driver_id
    """

    async def connect(self):
        query = self.scope.get("query_string").decode("utf-8")
        if query.startswith("token="):
            list_query = query.split("&")
            if len(list_query) < 2:
                await self.send(text_data=json.dumps({"message": "operator token va driver id kirtilishi shart"}))
            token = list_query[0].replace("token=", "")
            driver_id = list_query[1].replace("driver_id=", "")
            self.scope["driver_id"] = driver_id
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.scope["user_id"] = user_id
            except Exception as e:
                await self.close()

        await self.accept()
        await self.channel_layer.group_add("driver_location_group", self.channel_name)
        await self.send_initial_driver_loc_list()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("driver_location_group", self.channel_name)

    async def send_initial_driver_loc_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        if user.role == "operator":
            order_list = await self.get_locations_driver()
            await self.send(text_data=json.dumps(order_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga drivers location ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_driver_location(self, event):
        await self.send_initial_driver_loc_list()

    @sync_to_async
    def get_locations_driver(self):
        driver_id = self.scope["driver_id"]
        loc_object = DriverLocation.objects.filter(driver__id=driver_id).first()
        serializer = DriverLocationSerializer(loc_object)
        return serializer.data

    @sync_to_async
    def get_user_by_id(self, user_id):
        return Operators.objects.filter(id=user_id).first()
