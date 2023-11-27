from django.db import models

from user.models import CustomUser


class CarCategory(models.Model):
    type = models.CharField(max_length=100)
    minimum = models.PositiveIntegerField()
    waiting_cost = models.PositiveIntegerField(default=0)
    bonus_percent = models.PositiveIntegerField()
    baggage_cost = models.PositiveIntegerField()
    for_woman_cost = models.PositiveIntegerField()
    sum_for_per_km = models.PositiveIntegerField(default=1500)

    def __str__(self):
        return self.type


class Drivers(CustomUser):
    email = None
    is_staff = None
    is_active = None
    is_superuser = None
    password = None
    phone = models.CharField(max_length=15, unique=True)
    car_type = models.CharField(max_length=30)
    car_color = models.CharField(max_length=50)
    car_number = models.CharField(max_length=10)
    sms_code = models.CharField(max_length=30)
    sms_code_sent_date = models.DateTimeField(null=True, blank=True)
    confirmed = models.BooleanField(default=False)
    gender = models.CharField(max_length=15)
    balance = models.PositiveIntegerField(default=0)
    has_baggage = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        CarCategory,
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f"{self.first_name} - {self.phone}"

    class Meta:
        verbose_name = "Drivers"


class DriverLocation(models.Model):
    driver = models.ForeignKey(Drivers, related_name='driver_location', on_delete=models.CASCADE)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    bearing = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.driver.first_name
