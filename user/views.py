from datetime import datetime

from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg import openapi
from rest_framework.exceptions import PermissionDenied, NotFound, ParseError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

import random

from HeyCaby.eskiz import SendSmsApiWithEskiz
from user.models import CustomUser
from user.serializers import CustomTokenSerializer


# user tekshiruv
def user_chack(role):
    if role != 'user':
        raise PermissionDenied(detail='Only user roles are allowed!')


# parents tekshiruv
def driver_chack(role):
    if role != 'driver':
        raise PermissionDenied(detail='Only driver roles are allowed!')


# child tekshiruv
def operator_chack(role):
    if role != 'operator':
        raise PermissionDenied(detail='Only operator roles are allowed!')


# sms code uchun generate code
def generate_sms_code():
    return str(random.randint(10000, 99999))


class CustomUserTokenView(APIView):
    @swagger_auto_schema(request_body=CustomTokenSerializer, operation_description="username=phone")
    def post(self, request):
        """
        username = phone number
        """
        user = CustomUser.objects.filter(username=request.data.get('username')).first()
        if user is None:
            return Response({'error': 'User not found'}, status=404)
        refresh = RefreshToken.for_user(user)
        serialized_user = CustomTokenSerializer(user).data
        return Response({'refresh': str(refresh), 'access': str(refresh.access_token), 'user': serialized_user})

