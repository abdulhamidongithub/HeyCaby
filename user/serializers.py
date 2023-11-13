from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *


class CustomTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username',)


class OperatorTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'role')
        extra_kwargs = {
            'role': {'read_only': True}, 'id': {'read_only': True}
        }

