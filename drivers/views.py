from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.authentication import JWTAuthentication

from heycaby.eskiz import SendSmsApiWithEskiz
from drivers.models import Drivers, DriverLocation
from drivers.serializers import DriversSerializer, DriverLocationSerializer
from operators.models import Order, DriverPayment
from operators.serializers import OrderCreateSerializer
from user.views import generate_sms_code, driver_chack


class DriverProfilView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        driver_chack(request.user.role)

        drivers = Drivers.objects.filter(id=request.user.id).first()
        serializer = DriversSerializer(drivers)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)


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
            message = f"Kirakashgo mobil ilovasi uchun tasdiqlash kodingiz: {code}"
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
            return Response({'detail': 'Sms code is not active, it can only be active for 5 minute!',
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
                         'data': serializer.errors}, status=401)


class DriverAcceptOrder(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                          description='order_id = Buyurtmani id si')])
    def put(self, request):
        driver_chack(request.user.role)

        order_id = request.query_params.get('order_id')
        driver = Drivers.objects.filter(id=request.user.id).first()
        if driver.is_busy:
            return Response({'detail': 'Driverda tugatilmagan buyurtma bor',
                             'success': False}, status=401)
        if driver.category.driver_min_balance > driver.balance:
            return Response({'detail': 'Iltimos balancingizni toldiring',
                             'success': False}, status=401)

        order = Order.objects.filter(id=order_id).first()
        if order is None:
            return Response({'detail': 'Order not found',
                             'success': False}, status=404)
        if order.order_status == 'active':
            order.driver = driver
            order.order_status = 'accept'
            order.save()
            channel_layer = get_channel_layer()
            serializer = OrderCreateSerializer(order)
            async_to_sync(channel_layer.group_send)(
                "order_group",
                # WebSocket guruhi nomi (shu bo'yicha consumersdan qaysi websocketga jo'natish ajratib olinadi)
                {
                    "type": "add_new_order",
                    "order": serializer.data
                    # wensocket tomindagi yangi malumot kelganini qabul qilib oladigan funksiya
                },
            )

            async_to_sync(channel_layer.group_send)(
                "driver_location_group",
                {
                    "type": "add_new_driver_location",
                },
            )

            driver.is_busy = True
            driver.save()

            return Response({'success': True,
                             'first_name': order.driver.first_name,
                             'order_status': order.order_status,
                             'phone': order.driver.phone,
                             }, status=201)
        return Response({'detail': 'Buyurtma Activ emas',
                         'success': False}, status=404)


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
        if not order:
            return Response({'detail': 'Order not found',
                             'success': False}, status=404)

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
                         'success': False}, status=404)


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
        driver = Drivers.objects.filter(id=request.user.id).first()

        order = Order.objects.filter(id=order_id).first()
        if not order:
            return Response({'detail': 'Order not found',
                             'success': False}, status=404)

        if order.order_status == 'started' and order.driver.id == driver.id:
            order.order_status = 'finished'
            order.destination_lat = request.query_params.get('destination_lat')
            order.destination_long = request.query_params.get('destination_long')
            order.total_sum = request.query_params.get('total_sum')
            order.save()

            driver.is_busy = False
            driver.balance -= int(order.total_sum)*int(driver.category.percent)/100
            driver.save()

            DriverPayment.objects.create(amount=int(order.total_sum)*int(driver.category.percent)/100, driver=driver, status='yechib_olindi')

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "driver_location_group",
                {
                    "type": "add_new_driver_location",
                },
            )

            return Response({'success': True,
                             'first_name': order.driver.first_name,
                             'order_status': order.order_status,
                             'phone': order.driver.phone,
                             }, status=201)
        return Response({'detail': 'Buyurtma Activ emas',
                         'success': False}, status=401)


class DriverCancelOrder(APIView):
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
        if not order:
            return Response({'detail': 'Order not found',
                             'success': False}, status=404)

        if order.order_status == 'accept' and order.driver.id == request.user.id:
            order.driver = driver
            order.order_status = 'active'
            order.save()
            serializer = OrderCreateSerializer(order)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                "order_group",
                # WebSocket guruhi nomi (shu bo'yicha consumersdan qaysi websocketga jo'natish ajratib olinadi)
                {
                    "type": "add_new_order",
                    "order": serializer.data
                    # wensocket tomindagi yangi malumot kelganini qabul qilib oladigan funksiya
                },
            )

            async_to_sync(channel_layer.group_send)(
                "driver_location_group",
                {
                    "type": "add_new_driver_location",
                },
            )

            driver.is_busy = False
            driver.save()

            return Response({'success': True,
                             'first_name': order.driver.first_name,
                             'order_status': order.order_status,
                             'phone': order.driver.phone,
                             }, status=201)
        return Response({'detail': 'Buyurtma mavjud emas yoki bu Driverga ulanmagan',
                         'success': False}, status=401)


class TestIp(APIView):
    def get(self, request):
        ip = request.META.get("HTTP_X_FORWARDED_FOR")
        ip2 = request.META.get("REMOTE_ADDR")
        return Response({'ip': ip, "ip2": ip2})
