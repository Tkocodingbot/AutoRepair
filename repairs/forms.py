from . models import Repair
from django import forms

class RepairForm(forms.ModelForm):
    class Meta:
        model = Repair
        fields = ['Model_Name','Model_Year','Reg_Plate','Vin_Number','Millage','DashDasplay_Pic','Engine_Pic','Damage_pic1','Damage_pic2','Damage_pic3']
        widget = {
            'Model_Name' : forms.TextInput(attrs={'class':'form-control'}),
            'Model_Year' : forms.NumberInput(attrs={'class':'form-control'}),
            'Reg_Plate' : forms.NumberInput(attrs={'class':'form-control'}),
            'Vin_Number' : forms.NumberInput(attrs={'class':'form-control'}),
            'Millage' : forms.NumberInput(attrs={'class':'form-control'}),
            'DashDasplay_Pic' : forms.FileInput(attrs={'class':'form-control'}),
            'Engine_Pic' : forms.FileInput(attrs={'class':'form-control'}),
            'Damage_pic1' : forms.FileInput(attrs={'class':'form-control'}),
            'Damage_pic2' : forms.FileInput(attrs={'class':'form-control'}),
            'Damage_pic3' : forms.FileInput(attrs={'class':'form-control'}),
        }