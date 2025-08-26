from django.contrib import admin
from . models import TimeSlot,Booking,Invoice,Vehicle,Services,Quotation,QuotationRequest


admin.site.register(TimeSlot)
admin.site.register(Booking)
admin.site.register(Invoice)
admin.site.register(Vehicle)
admin.site.register(Services)
admin.site.register(Quotation)
admin.site.register(QuotationRequest)

