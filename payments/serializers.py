from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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

    def validate_type(self, value):
        if value not in ["Office", "Payme", "Click"]:
            raise ValidationError("The type should be one of these three: Payme/Click/Office")
        return value
