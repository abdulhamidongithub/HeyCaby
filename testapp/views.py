from asgiref.sync import async_to_sync
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from channels.layers import get_channel_layer


class IsmView(APIView):
    parser_classes = [MultiPartParser]  # Fayllarni qabul qilish uchun MultiPartParser qo'shamiz

    @swagger_auto_schema(request_body=IsmSerializer)
    def post(self, request):
        serializer = IsmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "ism_group",  # WebSocket guruhi nomi (shu bo'yicha consumersdan qaysi websocketga jo'natish ajratib olinadi)
                {
                    "type": "add_new_ism",   # wensocket tomindagi yangi malumot kelganini qabul qilib oladigan funksiya
                },
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
