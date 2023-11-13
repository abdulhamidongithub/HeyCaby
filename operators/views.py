from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from drivers.models import Drivers
from drivers.serializers import DriversSerializer
from operators.models import Operators
from operators.serializers import OperatorSerializer, OrderCreateSerializer
from user.views import operator_chack


# class OperatorCreateView(APIView):
#     @swagger_auto_schema(request_body=OperatorSerializer)
#     def post(self, request):
#         """
#         Operator create
#         """
#         serializer = OperatorSerializer(data=request.data)
#
#         if serializer.is_valid():
#
#             serializer.save(role='operator', )
#             return Response({'success': True,
#                              'data': serializer.data}, status=201)
#         return Response({'detail': 'Error',
#                          'success': False,
#                          'data': serializer.errors}, status=400)


class DriverCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DriversSerializer)
    def post(self, request):
        """
        Driver create
        """
        operator_chack(request.user.role)
        serializer = DriversSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']

            serializer.save(phone=username, role="driver")
            return Response({'detail': 'Created, sms code has been sent!',
                             'success': True,
                             'data': serializer.data}, status=201)
        return Response({'detail': 'Error',
                         'success': False,
                         'data': serializer.errors}, status=400)


class OperatorGet(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operator_chack(request.user.role)

        operators = Operators.objects.filter(id=request.user.id).first()
        serializer = OperatorSerializer(operators)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)


class DriversGetOperator(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operator_chack(request.user.role)

        drivers = Drivers.objects.all()
        serializer = DriversSerializer(drivers, many=True)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)


class OperatorDriverDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('driver_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='driver_id = Driver id'),
    ])
    def get(self, request):
        operator_chack(request.user.role)
        driver_id = request.query_params.get('driver_id')

        driver = Drivers.objects.filter(id=driver_id).first()
        serializer = DriversSerializer(driver)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)


class OrderCreate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=OrderCreateSerializer)
    def post(self, request):
        """
        Order create
        """
        operator_chack(request.user.role)
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():

            serializer.save(order_status="active")

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "order_group",
                # WebSocket guruhi nomi (shu bo'yicha consumersdan qaysi websocketga jo'natish ajratib olinadi)
                {
                    "type": "add_new_order",  # wensocket tomindagi yangi malumot kelganini qabul qilib oladigan funksiya
                },
            )
            return Response({'success': True,
                             'data': serializer.data}, status=201)
        return Response({'detail': 'Error',
                         'success': False,
                         'data': serializer.errors}, status=400)