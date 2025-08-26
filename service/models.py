from datetime import timezone
from django.db import models
from django.contrib.auth.models import User
from django.forms import ValidationError

class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=25, blank=True, null=True)
    model = models.CharField(max_length=15, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    vin_number = models.CharField(max_length=25, blank=True, null=True)
    license_plate = models.CharField(max_length=12, blank=True, null=True)
    
    def __str__(self):
        return f'{self.name} for {self.owner}'

class Services(models.Model):
    service_id = models.AutoField(primary_key=True, unique=True)
    service_type = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=50, blank=True, null=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return(self.service_type)
    
class QuotationRequest(models.Model):
    TRANSOPT = [
        ('manual','Manual'),
        ('automatic','Automatic')
    ]
    GASCHOICE = [
        ('petro','Petrol'),
        ('diesel','diesel'),
    ]
    
    quotereq_id = models.AutoField(primary_key=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)    
    vehicle_type = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    engine_capacity = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    gas = models.CharField(max_length=10, choices=GASCHOICE, blank=True, null=True)
    millage = models.CharField(max_length=6, blank=True, null=True)
    transmission = models.CharField(max_length=10, choices=TRANSOPT, default='manual',blank=True, null=True)
    service_requested = models.ForeignKey(Services,on_delete=models.CASCADE, blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    additional_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Quotation #{self.quotereq_id} for {self.user.username} it cost R{self.total_cost}"
    
class Quotation(models.Model):
    quote_id = models.AutoField(primary_key=True, unique=True) 
    quote_request = models.OneToOneField(QuotationRequest, on_delete=models.CASCADE)
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()

    def __str__(self):
        return f"Quotation for Request #{self.quote_id}"
    
class TimeSlot(models.Model):
    timeslot_id = models.AutoField(primary_key=True, unique=True) 
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%H:%M')}"
    def clean_time_slot(self):
        time_slot = self.cleaned_data.get('time_slot')
        if time_slot:
            if not TimeSlot.objects.filter(
                pk=time_slot.pk,
                is_available=True,
                start_time__gt=timezone.now()
            ).exists():
                raise ValidationError("This time slot is no longer available.")
        return time_slot

    
class Booking(models.Model):
    BOOKING_CHOICE = (
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('completed','Completed'),
        ('cancelled','Cancelled'),
    )
    booking_id = models.AutoField(primary_key=True, unique=True) 
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quotation = models.ForeignKey(QuotationRequest, on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_CHOICE, default='pending')
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['quotation'], 
                name='unique_quotation_booking'
            )
        ]
        indexes = [
            models.Index(fields=['time_slot']),
            models.Index(fields=['quotation']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f"Booking #{self.booking_id} for {self.user.username}"
    
class Invoice(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_number}"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Generate invoice number - you might want a better system
            last_invoice = Invoice.objects.order_by('id').last()
            last_id = last_invoice.id if last_invoice else 0
            self.invoice_number = f"INV-{str(last_id + 1).zfill(5)}"
        
        if not self.total_amount:
            self.total_amount = self.amount + self.tax_amount
            
        super().save(*args, **kwargs)

