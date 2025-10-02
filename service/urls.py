from django.urls import path
from . import views


from django.conf.urls.static import static
from django.conf import settings

app_name = 'service'
urlpatterns = [
    path('home/', views.home, name='home'),
    path('request/', views.GetQuote, name='request_quotation'),
    # path('request/success/', views.quotation_request_success, name='quotation_request_success'),
    path('my-quotations', views.my_quotations, name='my_quotations'),
    path('available-slots/', views.book_slot, name='available_slots'),
    path('confirmation/<int:booking_id>', views.booking_confirmation, name='booking_confirmation'),
    path('generate/<int:booking_id>', views.generate_invoice, name='generate_invoice'),
    path('my-invoices/', views.my_invoice, name='my_invoice'),
    path('vehicle/', views.add_vehicle, name='add_vehicle'),
    path('Cars/', views.Cars, name='Cars'),
    path('profile', views.EditProfileView, name='profile'), 
    path('vehicles/', views.vehicle_management, name='vehicle_management'),
    path('dashboard/', views.Dashboard, name='dashboard'),
    path('slot', views.Time_slot, name='slot'),
    path('bookings', views.bookings, name='bookings'),
    path('viewQuote/<int:quotereq_id>/', views.viewQuote, name='viewQuote'),
    path('tech', views.tech, name='tech'),
    path('userbooking',views.userbooking,name="userbooking"),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) 
# urlpatterns += static(settings.MEDIA_ROOT, document_root = settings.MEADIA_ROOT) 
