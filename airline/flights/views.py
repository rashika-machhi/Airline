from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponseRedirect
from . models import Flight,Airport,Passenger
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q 


# Create your views here.
#=================================== Main file =======================================
def index(request):
    return render(request,"users/login.html")

#=================================== Menu ============================================
def homepage(request):
    return render(request,'flights/homepage.html')

#=================================== Flight ==========================================
def get_airports():
    DataAirport = Airport.objects.all().order_by('city')
    return DataAirport

@login_required(login_url="/users/login")
def FlightList(request):
    Origin_List   =   get_airports().values('city').distinct()

    DataFlight_List = Flight.objects.all().order_by('origin__city')

    selected_origin   = request.GET.get('Origin')
    Search_For      = request.GET.get('search_query')

    if selected_origin:
        DataFlight_List = DataFlight_List.filter(origin__city=selected_origin)

    if Search_For:
        DataFlight_List = DataFlight_List.filter(Q(origin__city__icontains=Search_For) | Q(destination__city__icontains=Search_For) | Q(duration__icontains=Search_For))
        
    DataFlight_List= Paginator(DataFlight_List, settings.FETCH_LIST_SIZE)
    page_number = request.GET.get('page') 
    DataFlight_List = DataFlight_List.get_page(page_number) 
    totalpage = DataFlight_List.paginator.num_pages

    page_list = [TempFlight+1 for TempFlight in range(totalpage)]

    context = {'Origin_List': Origin_List,
                'LOCFlightList':DataFlight_List,
                'totalpagelist':page_list,
                'selected_filter': selected_origin,
                'search_query': Search_For,
    }
    return render(request, "flights/Flight_List.html", context)

@login_required(login_url="/users/login")
def addflight(request):   
    if request.method == "POST":
        data = request.POST
        origin_id = data.get('origin')
        destination_id = data.get('destination')
        duration = int(data.get('duration')) 

        if (duration == "" or duration <= 0):
            duration_error = "Duration must be a greater than 0"
            return render(request, 'flights/add_flight.html', {'duration_error': duration_error}) 
        
        if origin_id == destination_id:
            destination_error = "Source and destination cannot be the same."
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
            error_message = "Flight already exists with the same origin and destination."

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
            return redirect('/flights/Flight_List/')
          
    LOCAirport = get_airports()
    context = {'LOCAirport': LOCAirport}
    return render(request, 'flights/add_flight.html', context)

@login_required(login_url="/users/login")
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
        return redirect('/flights/Flight_List/')

    LOCAirport = get_airports()
    context = {'LOCAirport': LOCAirport,'flight':flight}
    return render(request, 'flights/add_flight.html', context)

def delete_flight(request,id):
    del_flight = Flight.objects.get(pk=id)
    del_flight.delete()
    return redirect("/flights/Flight_List/")

                 #======================= FlightDetails ======================= 

@login_required(login_url="/users/login")
def flight(request, flight_id):
    flight= Flight.objects.get(pk=flight_id)
    
    search_For = request.GET.get('search_query')
    if search_For:
        all_passengers = flight.passengers.filter(Q(first__icontains=search_For) | Q(last__icontains=search_For)) 
    else:
        all_passengers = flight.passengers.all().order_by('first')

    All_passenger_Rec= Paginator(all_passengers, settings.FETCH_LIST_SIZE) 
    page_number = request.GET.get('page')
    All_passenger_Rec = All_passenger_Rec.get_page(page_number)
    totalpage = All_passenger_Rec.paginator.num_pages 
    page_list = [passenger+1 for passenger in range(totalpage)]

    return render(request,"flights/flight.html",{
        "flight":flight,
        'totalpagelist':page_list,
        'passengers': All_passenger_Rec,
        "non_passengers": Passenger.objects.exclude(flights = flight).all().order_by('first'),
        'search_query': search_For

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
@login_required(login_url="/users/login")
def Airport_list(request):
    City_List   =   get_airports().values('city').distinct()

    AllAirport_Rec = Airport.objects.all().values().order_by('city') 

    selected_city   = request.GET.get('city')  # Get the selected filter value from POST data
    Search_For      = request.GET.get('search_query')

    if selected_city:
        AllAirport_Rec = AllAirport_Rec.filter(city=selected_city)
    
    if Search_For:
        AllAirport_Rec = AllAirport_Rec.filter(Q(city__icontains=Search_For) | Q(code__icontains=Search_For))    
        request.session['search_query'] = Search_For 

    if selected_city and not Search_For:
        # Clear the search query from the session if a filter is applied without a search query
        request.session.pop('search_query', None)

    AllAirport_Rec= Paginator(AllAirport_Rec, settings.FETCH_LIST_SIZE) 
    page_number = request.GET.get('page') 
    AllAirport_Rec = AllAirport_Rec.get_page(page_number) 

    totalpage = AllAirport_Rec.paginator.num_pages 

    page_list = [airport+1 for airport in range(totalpage)]

    context={
        'City_List': City_List,
        'airports': AllAirport_Rec,
        'totalpagelist':page_list,
        'selected_filter': selected_city,
        'search_query': Search_For
    }
    
    return render(request, "flights/Airport_list.html", context)

    

@login_required(login_url="/users/login")
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
        return redirect('Airport_list')

    return render(request, 'flights/add_airport.html')

@login_required(login_url="/users/login")
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
        success_message = "from message.success Airport has been successfully updated."

        messages.success(request, success_message)
        return redirect('Airport_list')
    
    context = {'airport': airport,'page_type': 'update'}
    return render(request, 'flights/add_airport.html', context)

def delete_airport(request,id):
    pi = Airport.objects.get(pk=id)
    pi.delete()
    return redirect("Airport_list")

#=================================== Passenger =========================================
def get_passengers():
    DataPassenger = Passenger.objects.all().order_by('first')
    return DataPassenger

@login_required(login_url="/users/login")
def Passenger_list(request):
    Passenger_List   =   get_passengers().values('first').distinct()
    AllPassenger_Rec = Passenger.objects.all().values().order_by('first')
    
    selected_first   = request.GET.get('first')  # Get the selected filter value from POST data
    Search_For      = request.GET.get('search_query')

    if selected_first:
        AllPassenger_Rec = AllPassenger_Rec.filter(first=selected_first)

    if Search_For:
        AllPassenger_Rec = AllPassenger_Rec.filter(Q(first__icontains=Search_For) | Q(last__icontains=Search_For))    
        request.session['search_query'] = Search_For 

    if selected_first and not Search_For:
        # Clear the search query from the session if a filter is applied without a search query
        request.session.pop('search_query', None)

    AllPassenger_Rec= Paginator(AllPassenger_Rec, settings.FETCH_LIST_SIZE)
    page_number = request.GET.get('page') 
    AllPassenger_Rec = AllPassenger_Rec.get_page(page_number)
    totalpage = AllPassenger_Rec.paginator.num_pages 

    #Creates a list of page numbers.
    page_list = [passenger+1 for passenger in range(totalpage)]

    context = {'Passenger_List': Passenger_List,
             'passengers': AllPassenger_Rec,
            'totalpagelist':page_list,
            'selected_filter': selected_first,
            'search_query': Search_For
               }
    return render(request,'passenger/Passenger_list.html',context)

@login_required(login_url="/users/login")
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
        return redirect('Passenger_list')
    
    queryset = Passenger.objects.all()
    context = {'add_passenger': queryset,'page_type': 'add',}
    return render(request,'passenger/add_passenger.html',context)

@login_required(login_url="/users/login")
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
        return redirect('Passenger_list')
    
    context = {'passenger': passenger,'page_type': 'update',}
    return render(request, 'passenger/add_passenger.html', context)

def delete_passenger(request,id):
    del_passenger = Passenger.objects.get(pk=id)
    del_passenger.delete()
    return redirect("Passenger_list")




