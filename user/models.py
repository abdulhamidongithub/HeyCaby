from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class CustomUser(AbstractUser):
    # first_name = None
    # last_name = None
    role = models.CharField(max_length=50, choices=(
        ('user', 'user'),
        ('driver', 'driver'),
        ('operator', 'operator')
    ))

    def __str__(self):
        return f"{self.first_name} {self.username} {self.role}"


# class CustomUser2(AbstractUser):
#     username = None
#     password = None
#     last_name = None
#     email = None
#     is_staff = None
#     is_active = None
#     date_joined = None
#     is_superuser = None
#     _groups = None
#     _user_permissions = None
#     last_login = None
#     groups = None
#     user_permissions = None
#     role = models.CharField(max_length=50, choices=(
#         ('user', 'user'),
#         ('driver', 'driver'),
#         ('operator', 'operator')
#     ))
#
#     def __str__(self):
#         return f"{self.first_name}"
