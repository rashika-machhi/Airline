from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from flights import views
from flights.views import index as idx

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    return render(request,"flights/option.html")  

def user(request):
    return render(request,"users/user.html")
 
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request,username = username, password = password)
        if user is not None:
            login(request, user)
            # url('flight/', idx, name="flight")
            # return render(request,'flights/option.html')
            return HttpResponseRedirect(reverse("options"))
            # return index(request)
            # return redirect('flights:index')
            # return redirect(index)
        else:
            return render(request,"users/login.html",{
                "message":"Invalid Credential."
            })
    return render(request,"users/login.html")

def logout_view(request):
    logout(request)
    # return render(request, "users/login.html",{
    #     "message":"Logged out."
    # })
    return redirect('login')
    