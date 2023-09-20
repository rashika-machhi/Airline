from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from . models import Flight,Airport,Passenger
from django.urls import reverse
from django.contrib import messages
import time


# Create your views here.
#=================================== Main file =======================================
def index(request):
    return render(request,"users/login.html")

#=================================== Menu ============================================
def homepage(request):
    return render(request,'flights/homepage.html')

#=================================== Flight ==========================================
def FlightList(request):
    #DataFlight_List = Flight.objects.select_related('origin').order_by('origin__city')
    DataFlight_List = Flight.objects.all().order_by('origin__city')
    context = {'LOCFlightList':DataFlight_List,}
    return render(request, "flights/Flight_List.html", context)

def get_airports():
    DataAirport = Airport.objects.all().order_by('city')
    return DataAirport

def addflight(request):   
    if request.method == "POST":
        data = request.POST
        origin_id = data.get('origin')
        destination_id = data.get('destination')
        duration = int(data.get('duration')) 

        if (duration == "" or duration <= 0):
            duration_error = "Back-end_Duration must be a greater than 0"
            return render(request, 'flights/add_flight.html', {'duration_error': duration_error}) 
        
        if origin_id == destination_id:
            destination_error = "Back-end_Source and destination cannot be the same."
            return render(request, 'flights/add_flight.html', {'destination_error': destination_error})    
        
        context={
            'duration':duration,
            'origin_id': origin_id,
            'destination_id': destination_id,
            
        }
        try:
            existing_flight = Flight.objects.get(origin_id=origin_id, destination_id=destination_id)
            # Existing flight found with the same origin and destination

            LOCAirport = get_airports()
            error_message = "Back-end_Flight already exists with the same origin and destination."

            if (existing_flight.origin_id == origin_id) and (existing_flight.destination_id == destination_id):
                # Origin and destination remain the same, show the error message
                context['error_message'] = error_message
            else:
                # Origin or destination changed, remove the error message
                context['error_message'] = None
                
            context.update({
                'error_message': error_message,
                'LOCAirport': LOCAirport,
                'selected_origin': existing_flight.origin_id,
                'selected_destination': existing_flight.destination_id,
            })
            return render(request, 'flights/add_flight.html', context)

                
        except Flight.DoesNotExist:
            new_flight = Flight(origin_id=origin_id, destination_id=destination_id, duration=duration)
            new_flight.save()
            success_message = "Flight has been successfully added."
            messages.success(request, success_message)
            time.sleep(2)
            return redirect('/flights/Flight_List/')
          
    LOCAirport = get_airports()
    context = {'LOCAirport': LOCAirport}
    return render(request, 'flights/add_flight.html', context)

def updateflight(request, flight_id):
    flight = get_object_or_404(Flight, pk=flight_id)
    error_message =""
    if request.method == "POST":
        data = request.POST
        origin_id = data.get('origin')
        destination_id = data.get('destination')
        duration = int(data.get('duration'))

        if origin_id == destination_id:
            error_message = "Source and destination cannot be the same."
            context = {'flight': flight, 'error_message': error_message}
            return render(request, 'flights/add_flight.html', context)

        context={
            'duration':duration
        }

        try:
            existing_flight = Flight.objects.exclude(pk=flight_id).get(origin_id=origin_id, destination_id=destination_id)
            LOCAirport = get_airports()
            error_message = "Flight already exists with the same origin and destination."
            context = {'flight':flight,
                       'error_message': error_message,
                       'LOCAirport': LOCAirport,
                       'origin_id': origin_id,
                       'destination_id': destination_id,
                       'selected_origin': existing_flight.origin_id,
                       'selected_destination': existing_flight.destination_id,
                       }
            return render(request, 'flights/add_flight.html', context)
        
        except Flight.DoesNotExist:
            pass

        if duration <= 0:
            error_message = "Duration must be greater than zero."
            context = {'flight': flight, 'error_message': error_message}
            return render(request, 'flights/add_flight.html', context)

        origin = Airport.objects.get(pk=origin_id)
        destination = Airport.objects.get(pk=destination_id)

        flight.origin = origin
        flight.destination = destination
        flight.duration = duration
        flight.save()

        success_message = "Flight has been successfully updated."
        messages.success(request, success_message)
        time.sleep(2)
        return redirect('/flights/Flight_List/')

    LOCAirport = get_airports()
    context = {'LOCAirport': LOCAirport,'flight':flight}
    return render(request, 'flights/add_flight.html', context)


# def updateflight(request, flight_id):
#     flight = get_object_or_404(Flight, pk=flight_id)

#     if request.method == "POST":
#         data = request.POST
#         origin_id = data.get('origin')
#         destination_id = data.get('destination')
#         duration = int(data.get('duration'))

#         if origin_id == destination_id:
#             error_message = "Source and destination cannot be the same."
#             return render(request, 'flights/add_flight.html', {'error_message': error_message})

#         try:
#             existing_flight = Flight.objects.exclude(pk=flight_id).get(origin_id=origin_id, destination_id=destination_id)
#             error_message = "Flight already exists with the same origin and destination."
#             return render(request, 'flights/add_flight.html', {'error_message': error_message})
        
#         except Flight.DoesNotExist:
#             pass

#         if duration == 0:
#             error_message = "Duration cannot be zero."
#             return render(request, 'flights/add_flight.html', {'error_message': error_message})

#         origin = Airport.objects.get(pk=origin_id)
#         destination = Airport.objects.get(pk=destination_id)

#         flight.origin = origin
#         flight.destination = destination
#         flight.duration = duration
#         flight.save()
#         return redirect('/flights/Flight_List/')

#     DataAirport = Airport.objects.all().order_by('city')
#     context = {'flight': flight, 'LOCAirport': DataAirport}
#     return render(request, 'flights/add_flight.html', context)

def delete_flight(request,id):
    del_flight = Flight.objects.get(pk=id)
    del_flight.delete()
    return redirect("/flights/Flight_List/")

                 #======================= FlightDetails ======================= 
def flight(request, flight_id):
    flight= Flight.objects.get(pk=flight_id)
    return render(request,"flights/flight.html",{
        "flight":flight,
        "passengers":flight.passengers.all(),
        "non_passengers": Passenger.objects.exclude(flights = flight).all()
    })

def book(request,flight_id):
    if request.method == "POST":
        flight = Flight.objects.get(pk = flight_id)
        passenger = Passenger.objects.get(pk=int( request.POST["passenger"]))
        passenger.flights.add(flight)
        return HttpResponseRedirect(reverse("flight",args=(flight.id,)))

def remove(request,flight_id):
    if request.method == "POST":
        flight = Flight.objects.get(pk = flight_id)
        passenger = Passenger.objects.get(pk=int( request.POST["passenger"]))
        passenger.flights.remove(flight)
        return HttpResponseRedirect(reverse("flight",args=(flight.id,)))

#=================================== Airport ==========================================

def Airport_list(request):
    airport_lists = Airport.objects.all().values().order_by('city')
    context = {'airports':airport_lists,}
    return render(request, "flights/Airport_list.html", context)

# def add_airport(request):
#     if request.method == "POST":
#         data = request.POST
#         city = data.get('city')
#         code = data.get('code')
        
#         if not city or not code:
#             error_message = "City and code fields are required."
#             return render(request, 'flights/add_airport.html', {'error_message': error_message})

#         # try:
#         #     existing_airport = Airport.objects.get(code=code,city=city)
#         #     # print("airport_code:" + existing_airport.code)
#         #     # print("airport_city:" + existing_airport.city)
#         #     error_message = "An airport already exists with the same city and code."
#         #     context = {'error_message': error_message,
#         #                 'city':existing_airport.city,
#         #                 'code':existing_airport.code, 
#         #                 'existing_airport': existing_airport}
#         #     return render(request, 'flights/add_airport.html', context)
        
#         # except Airport.DoesNotExist:
#         #     pass

#         try:
#             existing_airport = Airport.objects.get(city=city)
#             error_message = "An airport already exists with the same city."
#             context = {'error_message': error_message,
#                         'city':existing_airport.city,
#                         'code':existing_airport.code, 
#                         'existing_airport': existing_airport}
#             return render(request, 'flights/add_airport.html', context)
        
#         except Airport.DoesNotExist:
#             pass

#         try:
#             existing_airport = Airport.objects.get(code=code)
#             error_message = "An airport already exists with the same code."
#             context = {'error_message': error_message,
#                        'city':city,
#                         'code':code, 
#                         'city':existing_airport.city,
#                         'code':existing_airport.code,
#                         'existing_airport': existing_airport 
#                         }
#             return render(request, 'flights/add_airport.html', context)
        
#         except Airport.DoesNotExist:
#             pass

#         Airport.objects.create(
#             city=city,
#             code=code,
#         )
#         success_message = "Airport has been successfully added."
#         messages.success(request, success_message)
#         time.sleep(2)
#         return redirect('Airport_list')

#     queryset = Airport.objects.all()
#     context = {'add_airport': queryset}
#     return render(request, 'flights/add_airport.html', context)

# def add_airport(request):
#     if request.method == "POST":
#         data = request.POST
#         city = data.get('city')
#         code = data.get('code')
        
#         if not city or not code:
#             error_message = "City and code fields are required."
#             return render(request, 'flights/add_airport.html', {'error_message': error_message, 'city': city, 'code': code})

#         try:
#             existing_airport = Airport.objects.get(code=code, city=city)
#             error_message = "An airport with the same code already exists for a different city."
#             return render(request, 'flights/add_airport.html', {'error_message': error_message, 'city': city, 'code': code})
        
#         except Airport.DoesNotExist:
#             pass

#         try:
#             existing_airport = Airport.objects.get(city=city)
#             error_message = "An airport already exists with the same city."
#             return render(request, 'flights/add_airport.html', {'error_message': error_message, 'city': city, 'code': code})
        
#         except Airport.DoesNotExist:
#             Airport.objects.create(
#                 city=city,
#                 code=code,
#             )
#             success_message = "Airport has been successfully added."
#             messages.success(request, success_message)
#             return redirect('Airport_list')

#     queryset = Airport.objects.all()
#     context = {'add_airport': queryset}
#     return render(request, 'flights/add_airport.html', context)

def add_airport(request):
    if request.method == "POST":
        data = request.POST
        city = data.get('city')
        code = data.get('code')
        
        if not city or not code:
            error_message = "City and code fields are required."
            return render(request, 'flights/add_airport.html', {'error_message': error_message})
        
        context={
            'city':city,
            'code':code,
        }

        try:
            existing_airport = Airport.objects.get(code=code,city=city)
            error_message = "An airport already exists with the same code."
            context.update({
                'error_message': error_message, 
                'page_type': 'add', 
            })
            return render(request, 'flights/add_airport.html', context)
        
        except Airport.DoesNotExist:
            pass

        try:
            existing_airport = Airport.objects.get(city=city)
            city_error = "An airport already exists with the same city."
            context.update({
                'city_error': city_error, 
                'page_type': 'add',
            })
            return render(request, 'flights/add_airport.html', context)
        
        except Airport.DoesNotExist:
            pass

        try:
            existing_airport = Airport.objects.get(code=code)
            code_error = "An airport already exists with the same code."
            context.update({
                'code_error': code_error,  
                'page_type': 'add',
            })
            return render(request, 'flights/add_airport.html', context)
        
        except Airport.DoesNotExist:
            pass

        Airport.objects.create(
            city=city,
            code=code,
        )
        success_message = "Airport has been successfully added."
        messages.success(request, success_message)
        time.sleep(2)
        return redirect('Airport_list')

    return render(request, 'flights/add_airport.html')

def update_airport(request, id):
    airport = get_object_or_404(Airport, pk=id)
    if request.method == "POST":
        city = request.POST.get('city')
        code = request.POST.get('code')

        context={
            'city':city,
            'code':code,
        }

        try:
            existing_airport = Airport.objects.exclude(pk=id).get(city=city, code=code)
            error_message = "Airport already exists with the same city and code."
            context.update({
                'error_message': error_message,
                
                'page_type': 'update',
                
            })
            return render(request, 'flights/add_airport.html', context)
    
        except Airport.DoesNotExist:
            pass

        try:
            existing_airport = Airport.objects.exclude(pk=id).get(code=code)
            code_error = "Same code already exists have another city."
            context.update({
                'code_error': code_error,
                'page_type': 'update',
                
            })
            return render(request, 'flights/add_airport.html', context)
        
        except Airport.DoesNotExist:
            pass

        try:
            existing_airport = Airport.objects.exclude(pk=id).get(city=city)
            city_error = "Same code already exists have another city."
            context.update({
                'city_error': city_error,
                'page_type': 'update',
                
            })
            return render(request, 'flights/add_airport.html', context)
        
        except Airport.DoesNotExist:
            pass

        
        airport.city = city
        airport.code = code
        airport.save()
        success_message = "Airport has been successfully updated."

        messages.success(request, success_message)
        time.sleep(2)
        return redirect('Airport_list')
    
    context = {'airport': airport,'page_type': 'update'}
    return render(request, 'flights/add_airport.html', context)

def delete_airport(request,id):
    pi = Airport.objects.get(pk=id)
    pi.delete()
    return redirect("Airport_list")

#=================================== Passenger =========================================

def Passenger_list(request):
    passenger_lists = Passenger.objects.all().values().order_by('first')
    context = {'passengers':passenger_lists,}
    return render(request,'passenger/Passenger_list.html',context)

# def add_passenger(request):
#     if request.method == "POST":
#         data = request.POST
#         first = data.get('first')
#         last = data.get('last')
        
#         if first == "":
#             error_message = "firstname can not be empty "
#             return render(request, 'passenger/add_passenger.html', {'error_message': error_message})
        
#         if last == "":
#             error_message = "lastname can not be empty "
#             return render(request, 'passenger/add_passenger.html', {'error_message': error_message})

#         Passenger.objects.create(
#             first = first.capitalize(),
#             last = last.capitalize(),
#         )
#         success_message = "Passenger added successfully."
#         messages.success(request, success_message)
#         time.sleep(2)
#         return redirect('/flights/Passenger_list/')

    
#     queryset = Passenger.objects.all()
#     context = {'add_passenger': queryset}
#     return render(request,'passenger/add_passenger.html',context)

# def update_passenger(request, id):
#     passenger = get_object_or_404(Passenger, pk=id)
    
#     if request.method == 'POST':
#         first = request.POST.get('first')
#         last = request.POST.get('last')

#         if first == "":
#             error_message = "firstname can not be empty "
#             return render(request, 'passenger/add_passenger.html', {'error_message': error_message})
        
#         if last == "":
#             error_message = "lastname can not be empty "
#             return render(request, 'passenger/add_passenger.html', {'error_message': error_message})
        
#         passenger.first = first
#         passenger.last = last
#         passenger.save()
        
#         success_message = "Passenger updated successfully."
#         messages.success(request, success_message)
#         time.sleep(2)
#         return redirect('Passenger_list')
    
#     context = {'passenger': passenger}
#     return render(request, 'passenger/add_passenger.html', context)


def add_passenger(request):
    if request.method == "POST":
        data = request.POST
        first = data.get('first')
        last = data.get('last')
        context={
            'first':first,
            'last':last
        }
        if first == "":
            first_error_message = "firstname can not be empty "
            context.update({
                'first_error_message':first_error_message,
                'page_type': 'add',
            })
            return render(request, 'passenger/add_passenger.html', context)
        
        if last == "":
            last_error_message = "lastname can not be empty "
            context.update({
                'last_error_message':last_error_message,
                'page_type': 'add',
            })
            return render(request, 'passenger/add_passenger.html', context)

        Passenger.objects.create(
            first = first,
            last = last,
        )
        success_message = "Passenger Added successfully."
        messages.success(request, success_message)
        time.sleep(2)
        return redirect('Passenger_list')
    
    queryset = Passenger.objects.all()
    context = {'add_passenger': queryset,'page_type': 'add',}
    return render(request,'passenger/add_passenger.html',context)

def update_passenger(request, id):
    passenger = get_object_or_404(Passenger, pk=id)
    
    if request.method == 'POST':
        first = request.POST.get('first')
        last = request.POST.get('last')

        context={
            'first':first,
            'last':last,
        }

        if first == "":
            first_error_message = "firstname can not be empty "
            context.update({
                'first_error_message':first_error_message,
                'page_type': 'update',
            })
            return render(request, 'passenger/add_passenger.html', context)
        
        if last == "":
            last_error_message = "lastname can not be empty "
            context.update({
                'last_error_message':last_error_message,
                'page_type': 'update',
            })
            return render(request, 'passenger/add_passenger.html', context)
        
        passenger.first = first
        passenger.last = last
        passenger.save()

        success_message = "Passenger updated successfully."
        messages.success(request, success_message)
        time.sleep(2)
        return redirect('Passenger_list')
    
    context = {'passenger': passenger,'page_type': 'update',}
    return render(request, 'passenger/add_passenger.html', context)

def delete_passenger(request,id):
    del_passenger = Passenger.objects.get(pk=id)
    del_passenger.delete()
    return redirect("Passenger_list")




