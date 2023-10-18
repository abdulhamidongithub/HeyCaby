from clickuz.click_authorization import click_authorization
from clickuz.serializer import ClickUzSerializer
from clickuz.status import PREPARE, COMPLETE, AUTHORIZATION_FAIL_CODE, AUTHORIZATION_FAIL
from clickuz import ClickUz
from clickuz.views import ClickUzMerchantAPIView
from rest_framework.views import APIView


class ClickAPIView(APIView):
    def post(self, request):
        pass
