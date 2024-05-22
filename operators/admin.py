from django.contrib import admin

from .forms import OperatorAdminForm
from .models import *

admin.site.register(Client)
admin.site.register(Order)


class OperatorAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "first_name", "phone"]
    list_display_links = ('id', 'username')
    search_fields = ['username', 'first_name', 'phone']
    form = OperatorAdminForm


admin.site.register(Operators, OperatorAdmin)


class DriverPaymentAdmin(admin.ModelAdmin):
    list_display = ["id", "driver", "amount", "datetime"]
    list_display_links = ('id', 'driver')
    list_filter = ('datetime',)
    search_fields = ('driver', 'datetime')
    date_hierarchy = 'datetime'
    date_hierarchy_drilldown = False


admin.site.register(DriverPayment, DriverPaymentAdmin)

# class DriverPaymentAdmin(admin.ModelAdmin):
#     list_display = ["id", "driver", "amount", "datetime"]
#     list_display_links = ('id', 'driver')
#     list_filter = ('datetime',)
#     search_fields = ('driver', 'datetime')
#     date_hierarchy = 'datetime'
#     date_hierarchy_drilldown = False
#
#
# admin.site.register(DriverPayment, DriverPaymentAdmin)
