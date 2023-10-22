from clickuz.click_authorization import click_authorization
from clickuz.serializer import ClickUzSerializer
from clickuz.status import PREPARE, COMPLETE, AUTHORIZATION_FAIL_CODE, AUTHORIZATION_FAIL
from clickuz import ClickUz
from clickuz.views import ClickUzMerchantAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import PaymentSerializer
from .models import *

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
                    payments.filter(date = date)
                    | payments.filter(driver__fullname__contains = driver_name)
                    | payments.filter(driver__phone__contains = phone_num)
                    | payments.filter(reciever = reciever)
                    | payments.filter(type = type)
            )
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        payment = request.data
        serializer = PaymentSerializer(data=payment)
        serializer.is_valid(raise_exception=True)
        if payment.get("type") == "Office":
            serializer.save(completed=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

