from django.db import models

class CarCategory(models.Model):
    type = models.CharField(max_length=100)
    minimum = models.PositiveIntegerField()
    waiting_cost = models.PositiveIntegerField()
    bonus_percent = models.PositiveIntegerField()
    baggage_cost = models.PositiveIntegerField()

    def __str__(self):
        return self.type

class Driver(models.Model):
    fullname = models.CharField(max_length=40)
    phone = models.CharField(max_length=15)
    car_type = models.CharField(max_length=30)
    car_number = models.CharField(max_length=10)
    sms_code = models.CharField(max_length=30)
    confirmed = models.BooleanField(default=False)
    gender = models.CharField(max_length=15)
    balance = models.PositiveIntegerField(default=0)
    has_baggage = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(CarCategory, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.fullname} - {self.phone}"
