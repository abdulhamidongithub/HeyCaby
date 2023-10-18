from rest_framework import serializers

class PaymentSerializer(serializers.Serializer):
    amount = serializers.IntegerField()
    phone_number = serializers.CharField()

