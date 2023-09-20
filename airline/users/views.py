from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from flights import views
from django.contrib import messages
from flights.views import index as idx
from django.contrib.auth.models import User


# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request,"flights/homepage.html")  

def user(request):
    return render(request,"users/user.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username = username).exists():
            messages.error(request,"Invalid Username")
            context = {
                'username': username,
            }
            return render(request, "users/login.html", context)
        
        user = authenticate(username = username, password = password)

        if user is None:
            messages.error(request,'Invalid Password')
            context = {
                'username': username,
                'password': password
            }
            return render(request, "users/login.html", context)
        else:
            login(request, user)
            
            return redirect('/flights/homepage/')
            # return redirect('/')
        
    return render(request,"users/login.html")

def logout_view(request):
    logout(request)
    return render(request, "users/login.html")
    