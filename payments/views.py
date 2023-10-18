from clickuz.click_authorization import click_authorization
from clickuz.serializer import ClickUzSerializer
from clickuz.status import PREPARE, COMPLETE, AUTHORIZATION_FAIL_CODE, AUTHORIZATION_FAIL
from clickuz import ClickUz
from clickuz.views import ClickUzMerchantAPIView
from rest_framework.views import APIView

from .serializers import PaymentSerializer

# class ClickAPIView(APIView):
#     def post(self, request):
#         serializer = PaymentSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         valid_data = serializer.validated_data


