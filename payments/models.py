from django.db import models
from drivers.models import Driver

PAYMENT_TYPES = [
    ("Click", "Click"),
    ("Payme", "Payme"),
    ("Office", "Office"),
]

class Payment(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    type = models.CharField(
        max_length = 50,
        choices = PAYMENT_TYPES
    )
    reciever = models.CharField(
        max_length=30,
        blank = True
    )

    def __str__(self):
        return f"{self.driver.fullname} {self.amount}"