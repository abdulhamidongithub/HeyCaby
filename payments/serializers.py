from rest_framework import serializers

from .models import *

class PaymentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class PaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    driver = serializers.IntegerField()
    type = serializers.CharField()
    reciever = serializers.CharField()

