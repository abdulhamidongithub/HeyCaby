from django.db import models
from drivers.models import Drivers, CarCategory
from user.models import CustomUser


class Client(models.Model):
    phone = models.CharField(max_length=15)
    total_bonus = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.phone


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(Drivers, on_delete=models.SET_NULL, null=True)
    total_sum = models.PositiveIntegerField(default=0)
    baggage = models.BooleanField(default=False)
    for_women = models.BooleanField(default=False)
    is_comfort = models.BooleanField(default=False)
    client_phone = models.CharField(max_length=50)
    name_startin_place = models.CharField(max_length=255, blank=True, null=True)
    starting_point_long = models.CharField(max_length=50)
    starting_point_lat = models.CharField(max_length=50)
    order_status = models.CharField(max_length=50)
    destination_name = models.CharField(max_length=50, blank=True, null=True)
    destination_long = models.CharField(max_length=50, blank=True, null=True)
    destination_lat = models.CharField(max_length=50, blank=True, null=True)
    grading_point = models.PositiveSmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    waiting_seconds = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.id} : {self.order_status}"


class Operators(CustomUser):
    email = None
    is_staff = None
    is_superuser = None
    phone = models.CharField(max_length=15, unique=True)
    gender = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.first_name} - {self.phone}"

    class Meta:
        verbose_name = "Operators"


