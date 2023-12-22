from django.contrib import admin

from .models import *

admin.site.register(Client)
admin.site.register(Order)
admin.site.register(Operators)


class DriverPaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "driver", "amount", "datetime"]
    list_display_links = ('id', 'driver')


admin.site.register(DriverPayment, DriverPaymentAdmin)
