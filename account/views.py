# from pyexpat.errors import messages
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View
from .forms import UserRegistrationForm
from django.contrib.auth import logout as auth_logout, authenticate,login

from .models import Profile
 

class Signupuser(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, 'account/register.html', locals())
    
    def post(self, request):
        if request.user.is_authenticated:
            messages.warning(request, f"Account already logged in")
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username=form.cleaned_data.get("username")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            
            # user = authenticate(username=username, password=password)
            # login(request, user)
            messages.success(request,f"Congrdultions {username} your account is created successfully")
            
            # profile = Profile.objects.get(user=request.user)
            
            # profile.save()
            
            # return redirect("home")
        else :
            messages.warning(request, "Something went wrong, Try Again")
        return render(request, 'account/register.html',locals())
    
def logout(request):
    auth_logout(request)
    messages.success(request,f"You've successfully logged out")
    return redirect('home')