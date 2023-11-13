from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


class OperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operators
        fields = ('username', 'password', 'first_name', 'last_name', 'phone', 'gender', 'is_active', 'role')
        extra_kwargs = {
            'is_active': {'read_only': True},
            'role': {'read_only': True}
        }


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        extra_kwargs = {
            'order_status': {'read_only': True},
            'destination_long': {'read_only': True},
            'destination_lat': {'read_only': True},
            'grading_point': {'read_only': True},
            'waiting_seconds': {'read_only': True},
            'client': {'read_only': True},
            'driver': {'read_only': True},
            'total_sum': {'read_only': True},
        }

