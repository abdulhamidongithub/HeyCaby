from django.db import models
from drivers.models import Drivers

PAYMENT_TYPES = [
    ("Click", "Click"),
    ("Payme", "Payme"),
    ("Office", "Office"),
]


class Payment(models.Model):
    driver = models.ForeignKey(Drivers, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    date = models.DateField(auto_now_add=True)
    type = models.CharField(
        max_length=50,
        choices=PAYMENT_TYPES
    )
    reciever = models.CharField(
        max_length=30,
        blank=True
    )
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.driver.first_name} {self.amount}"
