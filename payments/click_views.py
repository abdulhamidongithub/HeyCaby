from clickuz import ClickUz
from clickuz.views import ClickUzMerchantAPIView
from django.db import transaction

from .models import *
from drivers.models import Drivers


class OrderCheckAndPayment(ClickUz):
    def check_order(self, order_id: str, amount: str, *args, **kwargs):
        driver = Drivers.objects.filter(phone=order_id)
        if not driver.exists():
            return self.ORDER_NOT_FOUND
        charge = Payment.objects.filter(driver__phone=order_id, amount=amount, type='Click')
        if charge.exists():
            charge = charge.last()
            if charge.amount == int(amount):
                return self.ORDER_FOUND
            else:
                charge.amount = int(amount)
                charge.completed = False
                charge.save()
                return self.ORDER_FOUND
        else:
            Payment.objects.create(
                driver=Drivers.objects.get(phone=order_id),
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
            driver = Drivers.objects.get(phone=order_id)
            driver.balance += int(transaction.amount)
            driver.save()
            return True
        else:
            return False


class ClickView(ClickUzMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment
