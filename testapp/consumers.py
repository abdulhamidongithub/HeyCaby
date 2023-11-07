from rest_framework_simplejwt.tokens import AccessToken

from drivers.models import Drivers
from .serializers import *
from asgiref.sync import sync_to_async
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Ism


class IsmlarConsumer(AsyncWebsocketConsumer):

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
        await self.channel_layer.group_add("ism_group", self.channel_name)
        await self.send_initial_ism_list()    # 1-martta Connect bo'lganda hamma malumotlar chiqishi

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("ism_group", self.channel_name)   # Connectlarni tugatish uchun

    async def send_initial_ism_list(self):
        user_id = self.scope['user_id']
        user = await self.get_user_by_id(user_id)
        if user.role == "driver":   # ismlarni korish uchun faqat superadmin role ga ruhsat berish
            ism_list = await self.get_ism_list()  # funksiya bo'yicha malumotlarni yuborish
            await self.send(text_data=json.dumps(ism_list))
        else:
            await self.send(text_data=json.dumps({"message": "Sizga ismlar ro'yxati ko'rish huquqi yo'q."}))

    async def add_new_ism(self, event):       # yangi malumot kelsa event qabul qiladi va shu yerdan yangi malumotlar yuboriladi
        await self.send_initial_ism_list()

    # asinxron qilib olish async def ichida sync ishlatib bomidi shunichun
    @sync_to_async
    def get_ism_list(self):        # ko'p joyda fodalanish uchun umumiy finksiya
        ism_objects = Ism.objects.all().order_by('-id')
        serializer = IsmSerializer(ism_objects, many=True)
        return serializer.data

    @sync_to_async
    def get_user_by_id(self, user_id):      # user malumotlarini olib olish
        return Drivers.objects.filter(id=user_id).first()