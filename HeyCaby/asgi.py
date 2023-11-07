import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HeyCaby.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
import testapp.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            testapp.routing.websocket_urlpatterns
        )
    )
})