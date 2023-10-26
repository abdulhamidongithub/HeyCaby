from clickuz.click_authorization import click_authorization
from clickuz.serializer import ClickUzSerializer
from clickuz.status import PREPARE, COMPLETE, AUTHORIZATION_FAIL_CODE, AUTHORIZATION_FAIL
from clickuz import ClickUz
from clickuz.views import ClickUzMerchantAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from paycomuz.views import MerchantAPIView
from paycomuz import Paycom
from paycomuz.models import Transaction

from .serializers import PaymentSerializer, PaymentReadSerializer
from .models import *
from driver.models import Driver

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
        serializer = PaymentReadSerializer(payments, many=True)
        return Response(serializer.data)

    def post(self, request):
        payment = request.data
        serializer = PaymentSerializer(data=payment)
        serializer.is_valid(raise_exception=True)
        valid_data = serializer.validated_data
        if payment.get("type") == "Office":
            Payment.objects.create(
                driver = Driver.objects.get(id=valid_data.get("driver")),
                amount = valid_data.get("amount"),
                type = valid_data.get("type"),
                reciever = valid_data.get("reciever"),
                completed = True
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif payment.get("type") == "Click":
            payment = Payment.objects.create(
                driver=Driver.objects.get(id=valid_data.get("driver")),
                amount=valid_data.get("amount"),
                type=valid_data.get("type"),
                reciever=valid_data.get("reciever"),
                completed = False
            )
            url = ClickUz.generate_url(
                order_id=str(payment.driver.phone),
                amount=str(payment.amount)
            )
            return Response({
                "link": url
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OrderCheckAndPayment(ClickUz):
    def check_order(self, order_id: str, amount: str, *args, **kwargs):
        driver = Driver.objects.filter(phone=order_id)
        if not driver.exists():
            return self.ORDER_NOT_FOUND
        charge = Payment.objects.filter(driver__phone=order_id, amount=amount, type='Click')
        if charge.exists():
            charge = charge.last()
            if charge.amount ==int(amount):
                return self.ORDER_FOUND
            else:
                charge.amount = int(amount)
                charge.completed = False
                charge.save()
                return self.ORDER_FOUND
        else:
            Payment.objects.create(
                driver=Driver.objects.get(phone=order_id),
                amount=int(amount),
                type="Click",
                completed=False
            )
            return self.ORDER_FOUND

    @transaction.atomic()
    def successfully_payment(self, order_id: str, transaction: object, *args, **kwargs):
        charge = Payment.objects.filter(driver__phone=order_id, completed=False)
        if charge.exists():
            charge = charge.last()
            charge.completed = True
            charge.save()
            driver = Driver.objects.get(phone=order_id)
            driver.balance += int(transaction.amount)
            driver.save()
            return True
        else:
            return False

class ClickView(ClickUzMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment

# Payme

class CheckOrder(Paycom):
    def check_order(self, amount, account, *args, **kwargs):
        driver = Driver.objects.filter(phone=account["order_id"])
        if not driver.exists():
            return self.ORDER_NOT_FOND
        charge = Payment.objects.filter(driver__phone=account["order_id"], completed=False)
        if charge.exists():
            charge = charge.last()
            if float(charge.amount) == float(amount) / 100:
                return self.ORDER_FOUND
            else:
                charge.amount = int((amount) / 100)
                charge.save()
                return self.ORDER_FOUND
        else:
            Payment.objects.create(
                driver=Driver.objects.get(phone=account["order_id"]),
                amount=int(amount),
                type="Payme",
                completed=False
            )
            return self.ORDER_FOUND


    def successfully_payment(self, account, transaction, *args, **kwargs):
        transaction = Transaction.objects.filter(_id=account["id"])
        if transaction.exists():
            charge = Payment.objects.filter(driver__phone=account["order_id"])
            if charge.exists():
                charge = charge.last()
                driver = Driver.objects.get(id=charge.driver.id)
                driver.balance += charge.amount
                driver.save()
                charge.completed = True
                charge.save()
                return True
            else:
                return False
        else:
            return False

    def cancel_payment(self, account, transaction, *args, **kwargs):
        transaction = Transaction.objects.filter(_id=account["id"])
        if transaction.exists():
            charge = Payment.objects.filter(driver__phone=account.get('order_id'))
            if charge.exists():
                charge = charge.last()
                charge.delete()
                return True
            else:
                return False
        else:
            return False


class PaycomView(MerchantAPIView):
    VALIDATE_CLASS = CheckOrder
