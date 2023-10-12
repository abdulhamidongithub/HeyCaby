from django.db import models

class CarType(models.Model):
    type = models.CharField(max_length=100)
    minimum = models.PositiveIntegerField()
    waiting_cost = models.PositiveIntegerField()
    bonus_percent = models.PositiveIntegerField()
    baggage_cost = models.PositiveIntegerField()

    def __str__(self):
        return self.type
