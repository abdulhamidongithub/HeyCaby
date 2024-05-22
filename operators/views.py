from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from drivers.models import Drivers, CarCategory
from drivers.serializers import DriversSerializer, CarCategorySerializer
from operators.models import Operators, Order, DriverPayment
from operators.serializers import OperatorSerializer, OrderCreateSerializer, OrderGetSerializer, \
    DriverPaymentSerializer, DriverPaymentPostSerializer
from payments.models import Payment
from user.views import operator_chack
from utils.pagination import paginate


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
            return Response({'success': True,
                             'data': serializer.data}, status=201)
        return Response({'success': False,
                         'data': serializer.errors}, status=400)


class CarCategoriesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        operator_chack(request.user.role)

        categories = CarCategory.objects.all()
        serializer = CarCategorySerializer(categories, many=True)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)


class OrdersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description='status = Buyurtma holati (active, accept, started, finished)',
                          enum=['active', 'accept', 'started', 'finished']),
        openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('offset', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ])
    def get(self, request):
        operator_chack(request.user.role)

        status = request.query_params.get('status')
        if status:
            if status == "active":
                orders = Order.objects.filter(order_status=status).all()
            else:
                orders = Order.objects.filter(order_status=status).all()
        else:
            orders = Order.objects.all()
        serializer = OrderGetSerializer(orders, many=True)
        # return Response({'detail': 'Success', 'data': serializer.data}, status=200)
        return paginate(orders, OrderGetSerializer, request)


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

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('offset', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ])
    def get(self, request):
        operator_chack(request.user.role)

        drivers = Drivers.objects.all()
        serializer = DriversSerializer(drivers, many=True)
        # return Response({'detail': 'Success', 'data': serializer.data}, status=200)
        return paginate(drivers, DriversSerializer, request)


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
        if driver is None:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
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
                    "type": "add_new_order",
                    "order": serializer.data
                    # wensocket tomindagi yangi malumot kelganini qabul qilib oladigan funksiya
                },
            )
            return Response({'success': True,
                             'data': serializer.data}, status=201)
        return Response({'detail': 'Error',
                         'success': False,
                         'data': serializer.errors}, status=400)


class OrderDelete(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)])
    def delete(self, request):
        """
        Order delete
        """
        operator_chack(request.user.role)
        order = Order.objects.filter(id=request.query_params.get('order_id')).first()
        if order:
            order.delete()
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
            return Response({'detail': 'Deleted', 'success': True}, status=202)
        return Response({"detail": "Order not found"}, status=404)


class DriverDelete(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('driver_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)])
    def delete(self, request):
        """
        Driver delete
        """
        operator_chack(request.user.role)
        driver = Drivers.objects.filter(id=request.query_params.get('driver_id')).first()
        if driver:
            driver.delete()
            return Response({'detail': 'Deleted', 'success': True}, status=202)
        return Response({"detail": "Order not found"}, status=404)


class DriverUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=DriversSerializer,
        manual_parameters=[
            openapi.Parameter('driver_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True)])
    def put(self, request):
        """
        Driver update
        """
        operator_chack(request.user.role)

        try:
            driver = Drivers.objects.get(id=request.query_params.get('driver_id'))
        except Drivers.DoesNotExist:
            return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DriversSerializer(driver, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DriverPaymentPost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(request_body=DriverPaymentPostSerializer)
    def post(self, request):
        operator_chack(request.user.role)
        serializer = DriverPaymentPostSerializer(data=request.data)

        if serializer.is_valid():
            driver = serializer.validated_data['driver']
            driver.balance += serializer.validated_data['amount']
            driver.save()
            serializer.save(status='otkazildi')
            Payment.objects.create(
                driver=driver,
                amount=serializer.validated_data['amount'],
                type='Office',
                reciever='',
                completed=True
            )
            return Response({'success': True,
                             'data': serializer.data}, status=201)
        return Response({'detail': 'Error',
                         'success': False,
                         'data': serializer.errors}, status=401)


class DriverPaymenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                          description='status = Buyurtma holati (otkazildi, otkazildi)',
                          enum=['otkazildi', 'yechib_olindi'])
    ])
    def get(self, request):
        operator_chack(request.user.role)
        if request.query_params.get('status'):
            driver = DriverPayment.objects.filter(status=request.query_params.get('status')).all().order_by('-id')
        else:
            driver = DriverPayment.objects.all().order_by('-id')
        serializer = DriverPaymentSerializer(driver, many=True)
        return Response({'detail': 'Success', 'data': serializer.data}, status=200)

