from django.contrib import admin
from .models import Payment


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["driver", "amount", "date", "type", "reciever", "completed"]
    list_display_links = ("driver", "amount", "date", "type", "reciever", "completed")
    search_fields = ['driver', 'date']
    list_filter = ['completed', 'type']


admin.site.register(Payment, PaymentAdmin)
