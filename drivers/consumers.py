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


class OrdersConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        token = self.scope.get("query_string").decode("utf-8")
        if token.startswith("token="):
            token = token.replace("token=", "")    # tokenni o'zini ovolamiz
            # Tokenni tekshirib ko'rish
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.scope["user_id"] = user_id      # user id olindi
            except Exception as e:
                await self.close()      # Token sinab ko'rishda xatolik, ulanishni rad etish

        await self.accept()
        await self.channel_layer.group_add("order_group", self.channel_name)
        await self.send_initial_order_list()    # 1-martta Connect bo'lganda hamma malumotlar chiqishi

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("order_group", self.channel_name)   # Connectlarni tugatish uchun

    async def send_initial_order_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        if user.role == "driver":   # ismlarni korish uchun faqat superadmin role ga ruhsat berish
            order_list = await self.get_order_list()  # funksiya bo'yicha malumotlarni yuborish
            await self.send(text_data=json.dumps(order_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga drivers ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_order(self, event):       # yangi malumot kelsa event qabul qiladi va shu yerdan yangi malumotlar yuboriladi
        await self.send_initial_order_list()

    # asinxron qilib olish async def ichida sync ishlatib bomidi shunichun
    @sync_to_async
    def get_order_list(self):        # ko'p joyda fodalanish uchun umumiy finksiya
        order_objects = Order.objects.filter(order_status='active').all().order_by('-id')
        serializer = OrderCreateSerializer(order_objects, many=True)
        return serializer.data

    @sync_to_async
    def get_user_by_id(self, user_id):      # user malumotlarini olib olish
        return Drivers.objects.filter(id=user_id).first()


class DriversLocationConsumer(AsyncWebsocketConsumer):
    """
    Operator uchun hamma driverlar
    """
    async def connect(self):
        token = self.scope.get("query_string").decode("utf-8")
        if token.startswith("token="):
            token = token.replace("token=", "")  # tokenni o'zini ovolamiz
            # Tokenni tekshirib ko'rish
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.scope["user_id"] = user_id  # user id olindi
            except Exception as e:
                await self.close()  # Token sinab ko'rishda xatolik, ulanishni rad etish

        await self.accept()
        await self.channel_layer.group_add("driver_location_group", self.channel_name)
        await self.send_initial_driver_loc_list()  # 1-martta Connect bo'lganda hamma malumotlar chiqishi

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("driver_location_group", self.channel_name)  # Connectlarni tugatish uchun

    async def send_initial_driver_loc_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        if user.role == "operator":  # ismlarni korish uchun faqat superadmin role ga ruhsat berish
            drivers_list = await self.get_locations_list()  # funksiya bo'yicha malumotlarni yuborish
            await self.send(text_data=json.dumps(drivers_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga drivers location ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_driver_location(self, event):  # yangi malumot kelsa event qabul qiladi va shu yerdan yangi malumotlar yuboriladi
        await self.send_initial_driver_loc_list()

    # asinxron qilib olish async def ichida sync ishlatib bomidi shunichun
    @sync_to_async
    def get_locations_list(self):  # ko'p joyda fodalanish uchun umumiy finksiya
        loc_objects = DriverLocation.objects.all().order_by('-id')
        serializer = DriverLocationSerializer(loc_objects, many=True)
        return serializer.data

    @sync_to_async
    def get_user_by_id(self, user_id):  # user malumotlarini olib olish
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
            # Tokenni tekshirib ko'rish
            try:
                access_token = AccessToken(token)
                user_id = access_token['user_id']
                self.scope["user_id"] = user_id  # user id olindi
            except Exception as e:
                await self.close()  # Token sinab ko'rishda xatolik, ulanishni rad etish

        await self.accept()
        await self.channel_layer.group_add("driver_location_group", self.channel_name)
        await self.send_initial_driver_loc_list()  # 1-martta Connect bo'lganda hamma malumotlar chiqishi

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("driver_location_group", self.channel_name)  # Connectlarni tugatish uchun

    async def send_initial_driver_loc_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        if user.role == "operator":  # ismlarni korish uchun faqat superadmin role ga ruhsat berish
            order_list = await self.get_locations_driver()  # funksiya bo'yicha malumotlarni yuborish
            await self.send(text_data=json.dumps(order_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga drivers location ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_driver_location(self, event):  # yangi malumot kelsa event qabul qiladi va shu yerdan yangi malumotlar yuboriladi
        await self.send_initial_driver_loc_list()

    # asinxron qilib olish async def ichida sync ishlatib bomidi shunichun
    @sync_to_async
    def get_locations_driver(self):  # ko'p joyda fodalanish uchun umumiy finksiya
        driver_id = self.scope["driver_id"]
        loc_object = DriverLocation.objects.filter(driver__id=driver_id).first()
        serializer = DriverLocationSerializer(loc_object)
        return serializer.data

    @sync_to_async
    def get_user_by_id(self, user_id):  # user malumotlarini olib olish
        return Operators.objects.filter(id=user_id).first()
