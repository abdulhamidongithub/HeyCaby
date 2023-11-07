from rest_framework import serializers
from .models import *
from rest_framework.exceptions import ValidationError


class IsmSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ism
        fields = '__all__'

    def validate_rasm(self, value):
        allowed_extensions = ('.png', '.jpg', '.jpeg')
        if not value.name.lower().endswith(allowed_extensions):
            raise ValidationError("Fayl formati noto'g'ri. Faqat .png, .jpg yoki .jpeg formatlarni qabul qilinadi.")
        return value