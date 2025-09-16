from datetime import timezone
from . models import Technician, Vehicle,Services,Quotation,QuotationRequest,TimeSlot,Booking,Invoice
from django import forms
from django.core.exceptions import ValidationError

# class QuotationRequestForm(forms.ModelForm):
#     vehicle_type = forms.ModelChoiceField(queryset=Vehicle.objects.all())
#     services_requested = forms.ModelMultipleChoiceField(
#         queryset=Services.objects.all(),
#         widget=forms.CheckboxSelectMultiple
#     )

#     class Meta:
#         model = QuotationRequest
#         fields = ['vehicle_type','millage','engine_capacity', 'service_requested', 'additional_notes']
        
class QuotationRequestForm(forms.ModelForm):
    class Meta:
        model = QuotationRequest
        fields = ['engine_capacity','gas','millage','transmission','service_requested','additional_notes']
        widgets = {
            'transmission' : forms.RadioSelect,
            'gas' : forms.RadioSelect
        }

        
# class BookingForm(forms.ModelForm):
#     time_slot = forms.ModelChoiceField(
#         queryset=TimeSlot.objects.filter(is_available=True),
#         widget=forms.RadioSelect
#     )

#     class Meta:
#         model = Booking
#         fields = ['time_slot']

# class BookingForm(forms.ModelForm):
#     class Meta:
#         model = Booking
#         fields = ['time_slot'] # i've removed the Qoptation inside array

class BookingForm(forms.ModelForm):
    quotation = forms.ModelChoiceField(
        queryset=QuotationRequest.objects.none(),
        empty_label="Select a quotation",
        required=True
    )
    time_slot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.none(),
        empty_label="Select a time slot",
        required=True
    )
    
    class Meta:
        model = Booking
        fields = ['quotation', 'time_slot']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Only show quotations that belong to current user AND don't have existing bookings
            booked_quotation_ids = Booking.objects.filter(user=user).values_list('quotation_id', flat=True)
            
            self.fields['quotation'].queryset = QuotationRequest.objects.filter(user=user).exclude(quotereq_id__in=booked_quotation_ids)
            
            # Only show available time slots that aren't already booked
            booked_slot_ids = Booking.objects.values_list('time_slot_id', flat=True)
            self.fields['time_slot'].queryset = TimeSlot.objects.filter(is_available=True).exclude(timeslot_id__in=booked_slot_ids)


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'model', 'year', 'vin_number', 'license_plate']
        
# class TimeSlotForm(forms.ModelForm):
#     date = forms.DateTimeField(widget=forms.DateInput(attrs={'type':'date'}),input_formats=['%Y-%m-%d'])
#     start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}),input_formats=['%0-%0-%0'])
#     end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type':'time'}),input_formats=['%0-%0-%0'])
#     class Meta:
#         model = TimeSlot
#         fields = ['date','start_time','end_time']
#         Widget = {
#             'date':forms.DateInput(attrs={'type':'date'}),
#             'start_time': forms.TimeInput(attrs={'type':'time'}),
#             'end_time': forms.TimeInput(attrs={'type':'time'})
            
#         }

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['date', 'start_time', 'end_time']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select date'
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'placeholder': 'HH:MM'
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time', 
                'class': 'form-control',
                'placeholder': 'HH:MM'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time")
        
        return cleaned_data
    
class TechniciansForm(forms.ModelForm):
    class Meta:
        model = Technician
        fields = ['first_name','last_name','phone','email']