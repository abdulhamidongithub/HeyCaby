from django.db import models

class Client(models.Model):
    phone = models.CharField(max_length=15)
    total_bonus = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.phone

