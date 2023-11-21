from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication

from heycaby.eskiz import SendSmsApiWithEskiz
from drivers.models import Drivers, DriverLocation
from drivers.serializers import DriversSerializer, DriverLocationSerializer
from operators.models import Order
from user.models import CustomUser
from user.serializers import CustomTokenSerializer
from user.views import generate_sms_code, driver_chack


class DriverProfilView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver_chack(request.user.role)

        drivers = Drivers.objects.filter(id=request.user.id).first()
        serializer = DriversSerializer(drivers)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)

    # @swagger_auto_schema(request_body=DriversSerializer)
    # def put(self, request):
    #
    #     drivers = Drivers.objects.filter(id=request.user.id).first()
    #     if drivers:
    #         serializer = DriversSerializer(instance=drivers, data=request.data, partial=True)
    #         print(serializer.is_valid())
    #         if serializer.is_valid():
    #             # drivers.username = serializer.validated_data['username']
    #             # drivers.first_name = serializer.validated_data['first_name']
    #             # drivers.last_name = serializer.validated_data['last_name']
    #             # drivers.car_type = serializer.validated_data['car_type']
    #             # drivers.car_number = serializer.validated_data['car_number']
    #             # drivers.gender = serializer.validated_data['gender']
    #             # drivers.has_baggage = serializer.validated_data['has_baggage']
    #             # drivers.category = serializer.validated_data['category']
    #             serializer.save()
    #             return Response(serializer.data, status=status.HTTP_200_OK)
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #     return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)


class DriverLoginView(APIView):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('username', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='username = phone number'),
    ])
    def post(self, request):
        """
        Driver Login
        """
        username = request.query_params.get('username')
        driver = Drivers.objects.filter(username=username).first()

        if driver is None:
            return Response({'error': 'User not found'}, status=404)

        if driver.username != '911111111':
            code = generate_sms_code()
            message = f"Tasdiqlash kodingiz: {code}"
            phone = int(username)
            eskiz_api = SendSmsApiWithEskiz(message=message, phone=phone)
            eskiz_api.send()

            driver.sms_code = code
            driver.sms_code_sent_date = datetime.now()
            driver.confirmed = True
            driver.save()

        return Response({'detail': 'Sms code has been sent!',
                         'username': driver.username,
                         'role': driver.role,
                         'first_name': driver.first_name,
                         'success': True}, status=200)


class DriverChackSmsCodeView(APIView):
    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('username', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='username = phone number'),
        openapi.Parameter('sms_code', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='sms code'),
    ])
    def post(self, request):
        """
        Chack sms code
        """
        username = request.query_params.get('username')
        sms_code = request.query_params.get('sms_code')
        driver = Drivers.objects.filter(username=username).first()
        if driver is None:
            return Response({'error': 'User not found'}, status=404)

        # test
        if username == '911111111' and sms_code == '11111':
            return Response({'detail': 'Sms code is correct!',
                             'success': True}, status=200)

        if sms_code != driver.sms_code:
            return Response({'detail': 'Sms code is incorrect!', 'success': False}, status=422)
        if not driver.confirmed:
            return Response({'detail': 'Sms code is not active!', 'success': False}, status=403)
        yuborilgan_vaqt = (driver.sms_code_sent_date.minute * 60) + driver.sms_code_sent_date.second
        hozr = (datetime.now().minute * 60) + datetime.now().second
        if (hozr - yuborilgan_vaqt) >= 300:
            driver.confirmed = False
            driver.save()
            return Response({'detail': 'Sms code is not active, it can only be active for 1 minute!',
                             'success': False},
                            status=403)
        return Response({'detail': 'Sms code is correct!',
                         'success': True}, status=200)


class DriverLocationPost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DriverLocationSerializer)
    def post(self, request):
        """
        Driver location create
        """
        driver_chack(request.user.role)
        serializer = DriverLocationSerializer(data=request.data)

        if serializer.is_valid():
            driver = Drivers.objects.filter(id=request.user.id).first()
            location = DriverLocation.objects.filter(driver__id=driver.id).first()
            if location:
                location.longitude = serializer.validated_data['longitude']
                location.latitude = serializer.validated_data['latitude']
                location.bearing = serializer.validated_data['bearing']
                location.date = datetime.now()

                location.save()

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "driver_location_group",
                    {
                        "type": "add_new_driver_location",
                    },
                )

                return Response({'success': True,
                                 'data': serializer.data}, status=201)

            serializer.save(driver=driver, date=datetime.now())

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "driver_location_group",
                {
                    "type": "add_new_driver_location",
                },
            )
            return Response({'success': True,
                             'data': serializer.data}, status=201)
        return Response({'detail': 'Error',
                         'success': False,
                         'data': serializer.errors}, status=400)


class DriverAccaptOrder(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='order_id = Buyurtmani id si')])
    def put(self, request):
        driver_chack(request.user.role)

        order_id = request.query_params.get('order_id')
        driver = Drivers.objects.filter(id=request.user.id).first()

        order = Order.objects.filter(id=order_id).first()
        if order.order_status == 'active':
            order.driver = driver
            order.order_status = 'accept'
            order.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "order_group",
                # WebSocket guruhi nomi (shu bo'yicha consumersdan qaysi websocketga jo'natish ajratib olinadi)
                {
                    "type": "add_new_order",
                    # wensocket tomindagi yangi malumot kelganini qabul qilib oladigan funksiya
                },
            )
            return Response({'success': True,
                             'first_name': order.driver.first_name,
                             'order_status': order.order_status,
                             'phone': order.driver.phone,
                             }, status=201)
        return Response({'detail': 'Buyurtma Activ emas',
                         'success': False}, status=400)


class DriverStartOrder(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='order_id = Buyurtmani id si')])
    def put(self, request):
        driver_chack(request.user.role)

        order_id = request.query_params.get('order_id')
        driver = Drivers.objects.filter(id=request.user.id).first()

        order = Order.objects.filter(id=order_id).first()
        if order.order_status == 'accept' and order.driver.id == request.user.id:
            order.driver = driver
            order.order_status = 'started'
            order.save()
            return Response({'success': True,
                             'first_name': order.driver.first_name,
                             'order_status': order.order_status,
                             'phone': order.driver.phone,
                             }, status=201)
        return Response({'detail': 'Buyurtma mavjud emas',
                         'success': False}, status=400)


class DriverFinishedOrder(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='order_id = Buyurtmani id si'),
        openapi.Parameter('destination_lat', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='destination_lat = Buyurtma tugagan manzil'),
        openapi.Parameter('destination_long', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='destination_long = Buyurtma tugagan manzil'),
        openapi.Parameter('total_sum', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='total_sum = Buyurtmani summasi')
    ])
    def put(self, request):
        driver_chack(request.user.role)

        order_id = request.query_params.get('order_id')

        order = Order.objects.filter(id=order_id).first()
        if order.order_status == 'started' and order.driver.id == request.user.id:
            order.order_status = 'finished'
            order.destination_lat = request.query_params.get('destination_lat')
            order.destination_long = request.query_params.get('destination_long')
            order.total_sum = request.query_params.get('total_sum')
            order.save()
            return Response({'success': True,
                             'first_name': order.driver.first_name,
                             'order_status': order.order_status,
                             'phone': order.driver.phone,
                             }, status=201)
        return Response({'detail': 'Buyurtma Activ emas',
                         'success': False}, status=400)




