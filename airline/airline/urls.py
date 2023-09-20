from django.contrib import admin
from django.urls import path,include
from flights.views import homepage
# from users.views import login_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path("flights/",include("flights.urls")),
    path("users/",include("users.urls")),
    path('',homepage, name='homepage'), 
]