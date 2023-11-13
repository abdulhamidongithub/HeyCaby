import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'heycaby.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack
import testapp.routing
import drivers.routing


application = ProtocolTypeRouter({
    "http": django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            testapp.routing.websocket_urlpatterns + drivers.routing.websocket_urlpatterns
        )
    )
})