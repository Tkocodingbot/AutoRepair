from django.shortcuts import render
from . models import Repair
from . forms import RepairForm


def repair(request):
    
    if request.method =="GET":
        form = RepairForm()
        return render(request, 'repairs/home.html', {'form':form})
