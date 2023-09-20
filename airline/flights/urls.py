from django.urls import path
from . import views

urlpatterns = [
    #=================================== Main file =======================================
    path("",views.index,name="index"),

    #=================================== Menu ============================================
    path('homepage/', views.homepage, name='homepage'),

    #=================================== Flight ==========================================
    path('Flight_List/', views.FlightList, name='FlightList'),
    path('add_flight/', views.addflight, name='addflight'),
    path('edit-flight/<int:flight_id>/', views.updateflight, name='edit_flight'),
    path('delete-flight/<int:id>/',views.delete_flight,name="deleteflight"),
                    #======================= FlightDetails ======================= 
    path("<int:flight_id>",views.flight, name="flight"),
    path("<int:flight_id>/book",views.book, name="book"),
    path("<int:flight_id>/remove",views.remove, name="remove"), 

    #=================================== Airport ==========================================
    path('Airport_list/', views.Airport_list, name='Airport_list'),
    path('add_airport/', views.add_airport, name='add_airport'),
    path('update-airport/<int:id>/',views.update_airport,name="updateairport"),
    path('delete/<int:id>/',views.delete_airport,name="deleteairport"), 
    #path('filter-airport-data/', views.filter_airport_data, name='filter_airport_data'),
    
    #=================================== Passenger =========================================
    path('Passenger_list/', views.Passenger_list, name='Passenger_list'),
    path('add_passenger/', views.add_passenger, name='add_passenger'),
    path('update-passenger/<int:id>/',views.update_passenger,name="updatepassenger"),
    path('delete-passenger/<int:id>/',views.delete_passenger,name="deletepassenger"), 
    #path('filter-passenger-data/', views.filter_passenger_data, name='filter_passenger_data'),


]