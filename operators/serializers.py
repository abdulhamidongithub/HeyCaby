from rest_framework import serializers
from django.contrib.auth import get_user_model

from drivers.serializers import CarCategoryForOrderSerializer, DriversSerializer
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
            'grading_point': {'read_only': True},
            'waiting_seconds': {'read_only': True},
            'client': {'read_only': True},
            'driver': {'read_only': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        category = CarCategory.objects.all()
        category_serializer = CarCategoryForOrderSerializer(category, many=True)
        data['costs'] = category_serializer.data
        return data


class OrderGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderDriverGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        driver = Drivers.objects.filter(id=data.get('driver')).first()
        print(driver)
        driver_ser = DriversSerializer(driver)
        data['driver'] = driver_ser.data
        return data
