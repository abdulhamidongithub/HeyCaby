from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="HeyCaby Taxi app API",
      default_version='v1',
      description="Taxi app APIs for taxi drivers to get clients and calculate their cost based on the distances "
                  "between A to B destinations.",
      contact=openapi.Contact(email="contact@snippets.local"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('operators/', include('operators.urls')),
    path('drivers/', include('drivers.urls')),
    path('user/', include('user.urls')),
    path('payments/', include('payments.urls')),
]
