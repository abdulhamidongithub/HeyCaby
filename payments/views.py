from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from clickuz import ClickUz
from paycomuz import Paycom

from .serializers import PaymentSerializer, PaymentReadSerializer
from .models import *
from drivers.models import Drivers


class PaymentsAPIView(APIView):
    def get(self, request):
        payments = Payment.objects.all()
        phone_num = request.query_params.get("phone")
        type = request.query_params.get("type")
        reciever = request.query_params.get("reciever")
        driver_name = request.query_params.get("name")
        date = request.query_params.get("date")
        if date or type or phone_num or reciever or driver_name:
            payments = (
                    payments.filter(date=date)
                    | payments.filter(driver__fullname__contains=driver_name)
                    | payments.filter(driver__phone__contains=phone_num)
                    | payments.filter(reciever=reciever)
                    | payments.filter(type=type)
            )
        serializer = PaymentReadSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        payment = request.data
        serializer = PaymentSerializer(data=payment)
        serializer.is_valid(raise_exception=True)
        valid_data = serializer.validated_data
        if payment.get("type") == "Click":
            payment = Payment.objects.create(
                driver=Drivers.objects.get(id=valid_data.get("driver")),
                amount=valid_data.get("amount"),
                type=valid_data.get("type"),
                reciever=valid_data.get("reciever"),
                completed=False
            )
            url = ClickUz.generate_url(
                order_id=str(payment.driver.phone),
                amount=str(payment.amount)
            )
            return Response({
                "link": url
            }, status=status.HTTP_200_OK)
        elif payment.get("type") == "Payme":
            payment = Payment.objects.create(
                driver=Drivers.objects.get(id=valid_data.get("driver")),
                amount=valid_data.get("amount"),
                type=valid_data.get("type"),
                reciever=valid_data.get("reciever"),
                completed=False
            )
            paycom = Paycom()
            url = paycom.create_initialization(
                amount=payment.amount * 100,
                order_id=str(payment.driver.phone),
                return_url=""
            )
            return Response({
                "link": url
            }, status=status.HTTP_200_OK)
        else:
            Payment.objects.create(
                driver=Drivers.objects.get(id=valid_data.get("driver")),
                amount=valid_data.get("amount"),
                type=valid_data.get("type"),
                reciever=valid_data.get("reciever"),
                completed=True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
