from rest_framework import serializers
from django.contrib.auth import get_user_model

from drivers.models import Drivers, DriverLocation, CarCategory
from user.models import *
from user.serializers import CustomUserSerializer


class DriversSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drivers
        fields = ('id', 'username', 'first_name', 'last_name', 'role', 'phone', 'car_type', 'car_color',
                  'car_number', 'gender', 'balance', 'has_baggage', 'is_busy', 'category')
        extra_kwargs = {
            'id': {'read_only': True},
            ' ': {'read_only': True},
            'balance': {'read_only': True},
            'phone': {'read_only': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        category = data.get('category')
        if category:
            category = CarCategory.objects.filter(id=category).first()
            category_serializer = CarCategorySerializer(category)
            data['category'] = category_serializer.data
        return data

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.car_type = validated_data.get('car_type', instance.car_type)
        instance.car_color = validated_data.get('car_color', instance.car_type)
        instance.car_number = validated_data.get('car_number', instance.car_number)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.has_baggage = validated_data.get('has_baggage', instance.has_baggage)
        instance.is_busy = validated_data.get('is_busy', instance.is_busy)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        return instance


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = '__all__'
        extra_kwargs = {
            'driver': {'read_only': True},
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        driver = data.get('driver')
        driver = Drivers.objects.filter(id=driver).first()
        driver_ser = DriversSerializer(driver)
        data['driver'] = driver_ser.data
        return data


class CarCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CarCategory
        fields = '__all__'
        extra_kwargs = {
            'baggage_cost': {'read_only': True},
        }


class CarCategoryForOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarCategory
        fields = ('id', 'type', 'sum_for_per_km', 'waiting_cost')
