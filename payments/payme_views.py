from paycomuz.views import MerchantAPIView
from paycomuz import Paycom
from paycomuz.models import Transaction
from django.db import transaction

from .models import *
from driver.models import Driver

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

    @transaction.atomic()
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
