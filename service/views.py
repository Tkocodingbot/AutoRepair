# from pyexpat.errors import messages
from datetime import datetime, timezone
import logging
from django.contrib import messages
from django.http import Http404
from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views import View
from .models import QuotationRequest, Quotation, Services, Vehicle, TimeSlot, Booking,Invoice
from .forms import QuotationRequestForm, BookingForm, TechniciansForm, TimeSlotForm, VehicleForm

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

from account.models import Profile
from account.forms import ProfileForm
from django.http import Http404

from django.db import transaction, IntegrityError

from django.core.paginator import Paginator  # used in pagination
from django.db.models import Q  #used to apply queryset for search and filter 

from account.decorators import unauthenticated_user,allowed_users,admin_only



@login_required
def my_quotations(request):
    quotations = Quotation.objects.filter(request__user=request.user)
    return render(request, 'service/my_quotations.html', {'quotations': quotations})


    
@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'service/booking_confirmation.html', {'booking': booking})

@login_required
def generate_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user = request.user)
    
    # create or get existing invoice
    
    invoice, created = Invoice.objects.get_or_create(booking=booking, 
    defaults={'amount': booking.quotation.final_price,
              'tax_amount':booking.quotation.final_price * 0.15,
              'due_date': booking.time_slot.start_time.date(),
              }           
    )
    
    # send invoice via email
    
    if created:
        subject = f"Invoice #{invoice.invoice_number} for Your Vehicle Service"
        message = render_to_string('service/email_invoice.txt',{
            'invoice': invoice,
            'booking': booking,
            'user':request.user
        }) # to look for 'service/email_invoice.txt'
        
        html_message = render_to_string('service/email_invoice.html', {
            'invoice': invoice,
            'booking': booking,
            'user':request.user
        }) # to look for 'service/email_invoice.txt'
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
            html_message=html_message,
            fail_silently=False
        )
    return render(request, 'service/invoice_detail.html', {'invoice':invoice})

@login_required
def my_invoice(request):
    invoices = Invoice.objects.filter(booking__user=request.user)
    return render(request, 'service/my_invoice.html', {'invoices':invoices})


@login_required
def home(request):
    return render(request, 'service/home.html')

@login_required
def vehicle_management(request):
    # Handle form submission for adding a vehicle
    if request.method == 'POST':
        try:
            form = VehicleForm(request.POST)
            if form.is_valid():
                car = form.save(commit=False)
                car.owner = request.user
                car.save()
                return redirect('service:vehicle_management')
            else:
                # If form is invalid, show error
                cars = Vehicle.objects.filter(owner=request.user)
                return render(request, 'service/vehicle_management.html', {
                    'form': form,
                    'car': cars,
                    'error': 'There was an error with the entered information. Please try again.'
                })
        except ValueError:
            cars = Vehicle.objects.filter(owner=request.user)
            return render(request, 'service/vehicle_management.html', {
                'form': VehicleForm(),
                'car': cars,
                'error': 'There was an error with the entered information. Please try again.'
            })
    
    # For GET requests, show both form and vehicle list
    cars = Vehicle.objects.filter(owner=request.user)
    return render(request, 'service/vehicle_management.html', {
        'form': VehicleForm(),
        'car': cars
    })

@login_required
def add_vehicle(request):
    
    if request.method == 'GET':
        return render(request, 'service/vehicle.html', {'form':VehicleForm()})
    else:
        try:
            form = VehicleForm(request.POST)
            car = form.save(commit=False)
            car.owner = request.user
            car.save()
            return redirect('home')
        except ValueError:
            return render(request, 'service/vehicle.html', {'form':VehicleForm(), 'error': 'They was an error with entered information, Try again later'})
        
@login_required        
def Cars(request):
    car = Vehicle.objects.filter(owner = request.user)
    return render(request, 'service/cars.html', {'car': car})

def view_cars(request,vehicle_id):
    Vcar = get_object_or_404(Vehicle, user=request.user, pk=vehicle_id)
    if request.method == "GET":
        vform = VehicleForm(instance=Vcar, user=request.user)
    return render(request, 'service/profile.html', {'Vcar':Vcar, 'vform':vform})
         
@login_required
def EditProfileView(request):
    prof = get_object_or_404(Profile, user=request.user)
    if request.method == 'GET':
        form = ProfileForm(instance=prof)
        return render(request, 'service/profile.html',{'form':form, 'prof':prof})
    else:
        try:
            form = ProfileForm(request.POST, request.FILES, instance=prof)
            if form.is_valid():
                form.save()
                return redirect('service:home') 
        except ValueError:  
            return render(request, 'service/profile.html',{'form':form, 'prof':prof, 'error':'something went wrong'})
   

@login_required
def GetQuote(request):
    total_cost = None
    cars = Vehicle.objects.filter(owner=request.user)
    
    if not cars.exists():
        messages.warning(request, "You need to add a vehicle first before requesting a quotation.")
        # return redirect('add_vehicle')  # Redirect to where users can add vehicles
    
    if request.method == 'POST':
        form = QuotationRequestForm(request.POST)
        if form.is_valid():
            # Get the selected vehicle
            vehicle_id = request.POST.get('vehicle')
            if not vehicle_id:
                form.add_error(None, "Please select a vehicle")
                return render(request, 'service/request_quotation.html', {
                    'form': form, 
                    'cars': cars,
                    'total_cost': total_cost
                })
                
            try:
                vehicle = Vehicle.objects.get(vehicle_id=vehicle_id, owner=request.user)
            except Vehicle.DoesNotExist:
                form.add_error(None, "Invalid vehicle selected")
                return render(request, 'service/request_quotation.html', {
                    'form': form, 
                    'cars': cars,
                    'total_cost': total_cost
                })
            
            # Get cleaned form data to avoid string/int errors
            data = form.cleaned_data
            
            # Your cost calculation logic
            engine_capacity = float(data['engine_capacity'])
            gas = data['gas']
            millage = int(data['millage'])
            transmission = data['transmission']
            service_requested = data['service_requested']

            cost = 0

            # Engine capacity cost
            if 1.0 <= engine_capacity <= 1.6:
                cost += 200
            elif 1.8 <= engine_capacity <= 2.0:
                cost += 220
            elif 2.4 <= engine_capacity <= 3.0:
                cost += 260
            elif 3.5 <= engine_capacity <= 5.0:
                cost += 300
            else:
                cost += 350

            # Fuel type cost
            if gas == "petrol":
                cost += 95
            else:
                cost += 135

            # Mileage cost
            if millage <= 10000:
                cost += 0
            elif 10000 < millage <= 100000:
                cost += 250
            elif 100000 < millage <= 300000:
                cost += 350
            elif 300000 < millage <= 500000:
                cost += 450
            elif 500000 < millage <= 800000:
                cost += 600
            else:
                cost += 1000

            # Transmission cost
            if transmission == 'manual':
                cost += 0
            else:
                cost += 100
                
            # Service type cost (assuming Services model has a cost field)
            # If not, you might need to adjust this logic
            service_cost = 0
            if service_requested == 'Major Service':  # Adjust based on your Services model
                service_cost = 350
            elif service_requested == 'Minor Service':
                service_cost = 150
            cost += service_cost

            # Final total
            total_cost = cost

            # Save to database with the vehicle
            quote = form.save(commit=False)
            quote.user = request.user
            quote.vehicle_type = vehicle  # This sets the required field
            quote.total_cost = total_cost
            quote.save()
            
            messages.success(request, "Quotation created successfully!")
            return redirect('service:available_slots')
            # return redirect('quotation_detail', quote_id=quote.quotereq_id)  # Redirect to a success page
            
    else:  # GET request
        form = QuotationRequestForm()

    return render(request, 'service/request_quotation.html', {
        'form': form, 
        'cars': cars,
        'total_cost': total_cost
    })

@login_required
def book_slot(request):
    # Get available slots (excluding booked ones)
    booked_slot_ids = Booking.objects.values_list('time_slot_id', flat=True)
    slots = TimeSlot.objects.filter(is_available=True).exclude(timeslot_id__in=booked_slot_ids)
    
    # Get quotations that don't have existing bookings
    booked_quotation_ids = Booking.objects.filter(user=request.user).values_list('quotation_id', flat=True)
    
    quotes = QuotationRequest.objects.filter(user=request.user).exclude(quotereq_id__in=booked_quotation_ids).order_by('-created_at')

    if request.method == "POST":
        form = BookingForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                booking = form.save(commit=False)
                booking.user = request.user
                
                # Double-check that the slot is still available
                if Booking.objects.filter(time_slot=booking.time_slot).exists():
                    messages.error(request, "This time slot has already been booked. Please choose another one.")
                    return render(request, "service/available_slots.html", {"form": form, "quotes": quotes,"slots": slots})
                
                # Double-check that the quotation doesn't already have a booking
                if Booking.objects.filter(quotation=booking.quotation).exists():
                    messages.error(request, "This quotation already has a booking.")
                    return render(request, "service/available_slots.html", {"form": form, "quotes": quotes,"slots": slots})
                
                booking.save()
                
                # Mark the time slot as unavailable
                booking.time_slot.is_available = False
                booking.time_slot.save()
                
                messages.success(request, "Booking created successfully")
                # return redirect('booking_success')  # Redirect to success page
                
            except IntegrityError:
                messages.error(request, "This quotation already has a booking or the time slot is no longer available.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = BookingForm(user=request.user)
    
    return render(request, "service/available_slots.html", {"form": form,  "quotes": quotes,"slots": slots})

@login_required
@allowed_users(allowed_roles=['admin'])
def Dashboard(request):
    booking = Booking.objects.filter(status = "pending")
    P_booking = Booking.objects.filter(status='confirmed')
    
    return render(request, 'service/dashboard.html',{'booking':booking, 'P_booking':P_booking})

@login_required
def Time_slot(request):
    form = TimeSlotForm()
    if request.method == 'GET':
        return render(request, 'service/time.html', {'form':form})
    else:
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            form.save()  
            messages.success(request, "Time slot created successfully")  
        return render(request, 'service/time.html', {'form':form})
    
@login_required
def bookings(request):
    bookings_list = Booking.objects.select_related('time_slot', 'user').all().order_by('-created_at')
    
    # Apply filters
    #  
    status_filter = request.GET.get('status')
    search_filter = request.GET.get('search')
    
    # if date_filter:
    #     try:
    #         # Convert string to date object
    #         filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
    #         # Filter by date field - replace 'date_field' with your actual field name
    #         bookings = bookings_list.filter(date_field=filter_date)
    #     except (ValueError, TypeError):
    #         # Invalid date format, ignore the filter
    #         pass
    
    if status_filter:
        bookings_list = bookings_list.filter(status=status_filter)
    
    if search_filter:
        bookings_list = bookings_list.filter(
            Q(user__first_name__icontains=search_filter) |
            Q(user__last_name__icontains=search_filter) |
            Q(user__username__icontains=search_filter) |
            Q(time_slot__date__icontains=search_filter) |
            Q(status__icontains=search_filter)
        )
    
    # Pagination - 10 items per page
    paginator = Paginator(bookings_list, 10)
    page_number = request.GET.get('page')
    bookings = paginator.get_page(page_number)
    
    
    # # Get all bookings from the database
    # bookings = Booking.objects.all().order_by('-booking_date', '-booking_time')
    
    
    if request.method == 'GET':
        return render(request, 'service/bookings.html', {'bookings': bookings})
    
@login_required
def tech(request):
    if request.method == "POST":
        form = TechniciansForm(request.POST)   # pass POST data here
        if form.is_valid():                    # no arguments here
            form.save()
            # optionally redirect after save
            messages.success(request, "Technician created successfull!")
            return redirect('service:tech')  
    else:  # GET request
        form = TechniciansForm()               # empty form

    return render(request, 'service/tech.html', {'form': form})


def viewQuote(request, quotereq_id):
    vquote = get_object_or_404(QuotationRequest, quotereq_id=quotereq_id)
    if request.method == "GET":
        form = QuotationRequestForm(instance=vquote)
        
        return render(request,"service/tech.html",{'vquote':vquote, 'form':form})

@login_required
def userbooking(request):
    userbookings = Booking.objects.filter(user=request.user).select_related('quotation')
    return render(request, "service/userbookings.html", {'bookings': userbookings})




        
        