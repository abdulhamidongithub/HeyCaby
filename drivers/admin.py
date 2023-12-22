from django.contrib import admin

from .models import *


class DriverAdmin(admin.ModelAdmin):
    list_display = ["id", "first_name", "phone"]
    list_display_links = ('id', 'first_name')

admin.site.register(Drivers, DriverAdmin)
admin.site.register(CarCategory)
admin.site.register(DriverLocation)

