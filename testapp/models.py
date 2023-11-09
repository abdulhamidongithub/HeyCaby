from django.db import models


class Ism(models.Model):
    name = models.CharField(max_length=100)
    rasm = models.FileField(upload_to='ism/', blank=True, null=True)
