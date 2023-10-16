from django.db import models
from drivers.models import *

class Client(models.Model):
    phone = models.CharField(max_length=15)
    total_bonus = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.phone

class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    total_sum = models.PositiveIntegerField(default=0)
    finished = models.BooleanField(default=False)
    baggage = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    for_women = models.BooleanField(default=False)
    starting_point_long = models.CharField(max_length=50)
    starting_point_lat = models.CharField(max_length=50)
    destination_long = models.CharField(max_length=50)
    destination_lat = models.CharField(max_length=50)
    cancelled = models.BooleanField(default=False)
    grading_point = models.PositiveSmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    waiting_seconds = models.PositiveSmallIntegerField(default=0)


