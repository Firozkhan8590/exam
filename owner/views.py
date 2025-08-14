from django.shortcuts import render,redirect,get_object_or_404
from .models import flightowner,Hotel,aircraft,flight
from django.contrib import messages
from django.contrib.auth  import login,logout
from django.contrib.auth.hashers import make_password,check_password
from django.http import HttpResponse
from app.models import Booking,userregister
from django.utils import timezone
from datetime import timedelta
from collections import OrderedDict

# Create your views here.
def ownerindex(request):
    return render(request,'ownerindex.html')
def flightregister(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        email = request.POST.get('email')
        phonenumber = request.POST.get('phone')
        password = request.POST.get('password')
        confirmpassword = request.POST.get('confirmPassword')
        companyname = request.POST.get('company_name')
        business_registration_number = request.POST.get('business_registration_number')
        license_number = request.POST.get('license_number')
        years_in_operation = request.POST.get('years_of_operation')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        country = request.POST.get('country')
        number_of_aircrafts = request.POST.get('number_of_aircraft')
        flight_type = request.POST.get('flight_types')
        airline_code = request.POST.get('airline_code')
        airline_license = request.FILES.get('airline_license')
        government_id_proof = request.FILES.get('government_id_proof')
        registration_certificate = request.FILES.get('registration_certificate')

        if password != confirmpassword:
            messages.error(request, 'Password does not match')
            return redirect('flightregister')

        if flightowner.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('flightregister')
        if flightowner.objects.filter(airline_code=airline_code) is None:
            return redirect('flightlogin')

        user = flightowner.objects.create(
            fullname=fullname,
            email=email,
            phonenumber=phonenumber,
            password=make_password(password),
            Companyname=companyname,
            bussiness_registration_number=business_registration_number,
            license_number=license_number,
            years_of_operation=years_in_operation,
            address=address,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            number_of_aircrafts=number_of_aircrafts,
            flight_type=flight_type,
            airline_code=airline_code,
            airline_license=airline_license,
            government_id_proof=government_id_proof,
            registration_certificate=registration_certificate
        )
        user.save()
        messages.success(request, 'Registration successful. Please login.')
        return redirect('flightlogin')
    return render(request, 'flightregister.html')

def flightlogin(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user=flightowner.objects.get(email=email)
        except flightowner.DoesNotExist:
            messages.error(request,'invalid email')
            return redirect('flightlogin')
        if not user.is_approved:
            messages.warning(request, 'Your account is pending admin approval.')
            return render(request,'owner_pending.html')


        if check_password(password,user.password):
            messages.success(request,'login successfully')
            return redirect('flightdashboard',user_id=user.id)
        else:
            messages.error(request,'invalid username and password')
            return redirect('flightlogin')
        


    return render(request,'flightlogin.html')
def flightdashboard(request, user_id):
    user=flightowner.objects.get(id=user_id)
    recent_flights = flight.objects.order_by('-created_at')[:5]  # latest 5
    aircrafts=aircraft.objects.filter(owner=user)
    
    active_flight=flight.objects.filter(aircraft_type__owner=user,status__iexact='scheduled')
    
    bookings=Booking.objects.filter(flight_id__in=active_flight)
    totalbookings=bookings.count()
    # ... other context if any
    return render(request, 'flightdashboard.html', {
        'recent_flights': recent_flights,
        'user': user,
        'aircrafts':aircrafts,
        'active_flight':active_flight,
        'totalbookings':totalbookings
    })
def hotelregister(request):
    if request.method == 'POST':
        hotel_name = request.POST.get('hotel_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        registration_number = request.POST.get('registration_number')
        license_number = request.POST.get('license_number')
        total_rooms = request.POST.get('total_rooms')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        image=request.FILES.get('image')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('hotelregister')

        # Optional: check if em(ail already exists
        if Hotel.objects.filter(email=email).exists():
            messages.error(request,'please type the valid email')
            return redirect('hotelregister')

        
        hotel = Hotel.objects.create(
            hotel_name=hotel_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            registration_number=registration_number,
            license_number=license_number,
            total_rooms=total_rooms,
            password=make_password(password),
            image=image
        )
        hotel.save()
        messages.success(request, "Hotel registered successfully.")
        return redirect('hotellogin')

    return render(request, 'hotelregistration.html')
def hotellogin(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            hotel=Hotel.objects.get(email=email)
        except Hotel.DoesNotExist:
            messages.error(request,'invalid username')
            return redirect('hotellogin')
        if check_password(password,hotel.password):
            messages.success(request,'login successfully')
            return redirect('hoteldashboard',hotel_id=hotel.id)
        else:
            messages.error(request,'invalid usrname or password')
            return redirect('hotellogin')
    return render(request,'hotellogin.html')

from django.utils import timezone
from collections import OrderedDict
from datetime import timedelta
from django.shortcuts import render, get_object_or_404
from .models import Hotel, Room, Booking
import json

def hoteldashboard(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)

    # Filter rooms for this hotel only
    rooms = Room.objects.filter(hotel=hotel).select_related('room_type')

    # Room status
    total_rooms = rooms.count()
    available_rooms = rooms.filter(status='available').count()
    booked_rooms = rooms.filter(status='booked').count()
    unavailable_rooms = total_rooms - (available_rooms + booked_rooms)


    # Booking trends - last 7 days
    today = timezone.now().date()
    start_date = today - timedelta(days=6)
    date_range = [start_date + timedelta(days=i) for i in range(7)]

    booking_trends = OrderedDict()
    for date in date_range:
        count = Booking.objects.filter(hotel=hotel, booking_date__date=date).count()
        booking_trends[date.strftime('%b %d')] = count

    # Paginate recent bookings
    start = int(request.GET.get('start', 0))
    limit = 7
    end = start + limit

    recent_bookings = Booking.objects.filter(hotel=hotel).prefetch_related('guest').order_by('-booking_date')[start:end]


    for b in recent_bookings:
        print(b.payment_status)
        print(b.status)
    




    # Stats
    total_bookings = Booking.objects.filter(hotel=hotel).count()
    total_cancellations = Booking.objects.filter(hotel=hotel, payment_status='failed').count()
    total_check_ins = Booking.objects.filter(hotel=hotel).exclude(check_in=None).count()

    # Guests filtered from bookings
    guests = Booking.objects.filter(hotel=hotel).select_related('user').values('user__id', 'user__username').distinct()

    context = {
        'hotel': hotel,
        'rooms': rooms,
        'recent_bookings': recent_bookings,
        'total_bookings': total_bookings,
        'total_cancellations': total_cancellations,
        'total_check_ins': total_check_ins,
        'start': start,
        'limit': limit,
        'has_next': end < total_bookings,
        'has_previous': start > 0,

        # Chart data
        'available_rooms': available_rooms,
        'booked_rooms': booked_rooms,
        'unavailable_rooms': unavailable_rooms,
        'booking_labels': json.dumps(list(booking_trends.keys())),
        'booking_data': json.dumps(list(booking_trends.values())),

        # Guest data
        'guests': guests,
    }

    return render(request, 'hoteldashboard.html', context)



def hotel_logout(request):
    logout(request)
    return redirect('landing_page')
def aircraft_registration(request,user_id):
    user=flightowner.objects.get(id=user_id)
    if request.method=='POST':
        
        manufacturer=request.POST.get('manufacturer')
        model=request.POST.get('model')
        registation_number=request.POST.get('registration_number')
        seat_capacity=request.POST.get('seat_capacity')
        aircraft_image=request.FILES.get('aircraft_image')
        print("DEBUG >> Uploaded Image:", aircraft_image)
        flight=aircraft.objects.create(
            owner=user,
            manufacturer=manufacturer,
            model=model,
            registation_number=registation_number,
            seat_capacity=seat_capacity,
            aircraft_image=aircraft_image
        )
        flight.save()
        messages.success(request,'Aircraft is registered successfully')
        return redirect('flightdashboard',user_id=user.id)
    return render(request,'aircraft.html',{'user':user})
def view_aircraft(request, user_id):
    user = get_object_or_404(flightowner, id=user_id)
    aircrafts = aircraft.objects.filter(owner=user)
    for a in aircrafts:
        print("Image for", a.registation_number, ":", a.aircraft_image)
    return render(request, 'viewaircraft.html', {'flight': aircrafts, 'user': user})

def add_flight(request, user_id):
    user = flightowner.objects.get(id=user_id)
    plane = aircraft.objects.filter(owner=user)  # list of aircrafts for dropdown

    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        aircraft_id= request.POST.get('aircraft')  # Get from dropdown
        departure_airport = request.POST.get('departure_airport')
        arrival_airport = request.POST.get('arrival_airport')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        business_price = request.POST.get('business_class_price')
        economy_price = request.POST.get('economy_class_price')
        tax = request.POST.get('tax_percentage')

        duration = request.POST.get('flight_duration')
        status = request.POST.get('status')
        baggage_allowance = request.POST.get('baggage_allowance')
        if flight.objects.filter(flight_number=flight_number).exists():
            messages.error(request, f"Flight number '{flight_number}' already exists.")
            return redirect('add_flight', user_id=user.id)

        selected_aircraft = aircraft.objects.get(id=int(aircraft_id))  # convert to int

        flight.objects.create(
                
                    flight_number=flight_number,
                    aircraft_type=selected_aircraft,
                    departure_airport=departure_airport,
                    arrival_airport=arrival_airport,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    business_class_price=business_price,
                    economy_class_price=economy_price,
                    tax_percentage=tax,
                    duration=duration,
                    status=status,
                    baggage_allowance=baggage_allowance
        )

        
        

        messages.success(request, 'Flight added successfully')
        return redirect('flightdashboard', user_id=user.id)

    return render(request, 'addflight.html', {'user': user, 'plane': plane})
def view_flight(request,user_id):
    user=flightowner.objects.get(id=user_id)
    
    schedule=flight.objects.filter(aircraft_type__owner=user)
    return render(request,'viewflight.html',{'schedule':schedule,'user':user})
def update_flight(request,user_id,flight_id):
    user=flightowner.objects.get(id=user_id)
    plane=aircraft.objects.filter(owner=user)
    flights=flight.objects.get(id=flight_id)
    

    if request.method=='POST':
        flights.flight_number=request.POST.get('flight_number')
        aircraft_id=request.POST.get('aircraft_type')
        flights.aircraft_type=aircraft.objects.get(id=aircraft_id)
        flights.departure_airport=request.POST.get('departure_airport')
        flights.arrival_airport=request.POST.get('arrival_airport')
        flights.departure_time=request.POST.get('departure_time')
        flights.arrival_time=request.POST.get('arrival_time')
        flights.price=request.POST.get('price')
        flights.duration=request.POST.get('duration')
        flights.status=request.POST.get('status')
        flights.baggage_allowance=request.POST.get('baggage_allowance')
        
        flights.save()
        
        messages.success(request,'updated successfully')
        return redirect('flightdashboard',user_id=user.id)
    return render(request,'updateflight.html',{'user':user,'plane':plane,'flights':flights})
def flightlogout(request):
    return redirect('landing_page')
def delete_flight(request, user_id, flight_id):
    user = flightowner.objects.get(id=user_id)

    try:
        flight_to_delete = flight.objects.get(id=flight_id, aircraft_type__owner=user)

        # First, delete all bookings for this flight
        Booking.objects.filter(flight=flight_to_delete).delete()

        # Then delete the flight itself
        flight_to_delete.delete()

        messages.success(request, 'Flight and all related bookings deleted successfully.')

    except flight.DoesNotExist:
        messages.error(request, 'Flight not found or unauthorized access.')

    return redirect('flightdashboard', user_id=user_id)
def owner_view_bookings(request,user_id):
    owner = flightowner.objects.get(id=user_id)
    if not owner:
        return HttpResponse("You are not registered as a flight owner.")

    flights = flight.objects.filter(aircraft_type__owner=owner)
    bookings = Booking.objects.filter(flight__in=flights)
    

    return render(request, 'owner_view_bookings.html', {'booking': bookings})


#hotel searching using apis

import requests
from django.conf import settings
from django.shortcuts import render

# 🔹 Get access token
def get_access_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": settings.AMAD_API_KEY,
        "client_secret": settings.AMAD_API_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    print("✅ JSON keys:", response.json().keys())

    return response.json().get("access_token")


def search_hotels_by_citycode(city_code, checkin_date, checkout_date, adults=1):
    access_token = get_access_token()
    print("🪪 Access Token:", access_token)

    # Step 1: Get hotel IDs for the city
    hotel_lookup_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"cityCode": city_code}
    hotel_lookup_response = requests.get(hotel_lookup_url, headers=headers, params=params)

    hotel_ids = []
    if hotel_lookup_response.status_code == 200:
        data = hotel_lookup_response.json()
        hotel_ids = [h['hotelId'] for h in data.get("data", [])]
    else:
        print("❌ Hotel ID lookup failed:", hotel_lookup_response.text)
        return {"data": [], "error": "Hotel ID lookup failed"}

    if not hotel_ids:
        print("❌ No hotel IDs found for this city.")
        return {"data": [], "error": "No hotels found for this city."}

    # Step 2: Get hotel offers using hotelIds
    hotel_ids_param = ",".join(hotel_ids[:10])  # limit to 10 to avoid overflow
    offers_url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
    params = {
        "hotelIds": hotel_ids_param,
        "checkInDate": checkin_date,
        "checkOutDate": checkout_date,
        "adults": adults,
        "roomQuantity": 1,
        "paymentPolicy": "NONE",
        "includeClosed": False,
        "bestRateOnly": True,
        "view": "FULL",
        "sort": "PRICE",
        "currency": "INR"
    }

    response = requests.get(offers_url, headers=headers, params=params)
    print("📡 Amadeus API CALLED:", response.url)
    print("📄 Status Code:", response.status_code)
    print("📄 Response JSON:", response.json())

    try:
        return response.json()
    except Exception as e:
        print("❌ JSON Error:", str(e))
        return {"data": [], "error": str(e)}


# 🔹 City code mapping
city_codes = {
    "bengaluru": "BLR",
    "delhi": "DEL",
    "mumbai": "BOM",
    "kochi": "COK",
    "chennai": "MAA",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "goa": "GOI",
    "paris": "PAR"  # ✅ Amadeus always returns dummy data for testing with PAR
}

# 🔹 Django view
def hotel_search_view(request):
    if request.method == "POST":
        city = request.POST.get("city", "Bengaluru").lower()
        city_code = city_codes.get(city, "PAR")  # fallback to Paris for test data

        checkin = request.POST.get("checkin", "2025-07-10")
        checkout = request.POST.get("checkout", "2025-07-11")
        adults = int(request.POST.get("adults", 1))  # cast to int

        results = search_hotels_by_citycode(city_code, checkin, checkout, adults)
        hotels = results.get("data", [])
        error = results.get("error", "")

        print("📊 Hotels found:", len(hotels))

        return render(request, "hoteldisplay.html", {
            "hotels": hotels,
            "city": city.title(),
            "checkin": checkin,
            "checkout": checkout,
            "adults": adults,
            "error": error,
        })

    return render(request, "hoteldisplay.html", {"hotels": []})

from .models import HotelBooking, Room, RoomType, RoomFacility
from datetime import date
# add new booking of hotels
def add_new_booking(request, hotel_id):
    hotels = Hotel.objects.get(id=hotel_id)

    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        age = request.POST.get('age')
        checkin = request.POST.get('checkin_date')
        checkout = request.POST.get('checkout_date')
        guests = request.POST.get('guests')
        total_price = request.POST.get('total_price')

        HotelBooking.objects.create(
            hotel=hotels,
            customer_name=customer_name,
            age=age,
            checkin_date=checkin,
            checkout_date=checkout,
            guests=guests,
            total_price=total_price
        )

        messages.success(request, 'Booking added successfully ✅')
        return redirect('hoteldashboard',hotel_id=hotels.id)

    return render(request, 'new_booking.html', {'hotels': hotels,'today_date':date.today()})

def add_room_type(request,hotel_id):
    hotel=Hotel.objects.get(id=hotel_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if RoomType.objects.filter(hotel=hotel,name=name).exists():
            messages.warning(request,'room type is already exists')
            return redirect('add_room_type',hotel_id=hotel.id)
        RoomType.objects.create(hotel=hotel,name=name, description=description)
        messages.success(request, "Room type added successfully.")
        return redirect('hoteldashboard',hotel_id=hotel.id)  # or to room listing

    return render(request, 'add_room_type.html',{'hotel':hotel})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Hotel, Room, RoomType, RoomFacility, RoomImage,HotelSearch
from django.contrib import messages
from django.utils.dateparse import parse_date
from django.db.models import Min

def add_room(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    room_types = RoomType.objects.filter(hotel=hotel)

    if request.method == 'POST':
        room_type_id = request.POST.get('room_type')
        price_per_night = request.POST.get('price_per_night')
        amenities = request.POST.getlist('amenities')  # list of strings
        images = request.FILES.getlist('images')  # multiple image input

        room_type = RoomType.objects.get(id=room_type_id)

        # Create Room without image (image handled separately)
        room = Room.objects.create(
            hotel=hotel,
            room_type=room_type,
            price_per_night=price_per_night,
            status='available'
        )

        # Save Room Facilities
        for amenity in amenities:
            RoomFacility.objects.create(room=room, name=amenity)

        # Save multiple Room Images
        for img in images:
            RoomImage.objects.create(room=room, image=img)

        messages.success(request, 'Room added successfully ✅')
        return redirect('hoteldashboard', hotel_id=hotel.id)

    return render(request, 'addrooms.html', {
        'hotel': hotel,
        'room_types': room_types
    })

def manage_rooms(request,hotel_id):
    hotel=get_object_or_404(Hotel,id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel).select_related('room_type').prefetch_related('images')
    
    return render(request, 'manage_rooms.html', {
        'hotel': hotel,
        'rooms': rooms,
    })
def delete_rooms(request,hotel_id,room_id):
    hotel=get_object_or_404(Hotel,id=hotel_id)
    rooms=get_object_or_404(Room,id=room_id,hotel=hotel)
    rooms.delete()
    messages.success(request,'Deleted Successfully')
    return redirect('manage_rooms', hotel_id=hotel.id)
def manage_guests(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id)
    booking=GuestDetail.objects.filter(booking__hotel=hotel)
    

    # ✅ Optional filters
    today = timezone.now().date()
    filter_type = request.GET.get('filter')  # e.g., "today", "upcoming", "all"

    if filter_type == 'today':
        bookings = Booking.objects.filter(hotel=hotel, check_in=today)
    elif filter_type == 'upcoming':
        bookings = Booking.objects.filter(hotel=hotel, check_in__gt=today)
    else:
        bookings = Booking.objects.filter(hotel=hotel)
    if request.method == 'POST':
        search = request.POST.get('search', '').strip()
        guest_details = GuestDetail.objects.filter(
            booking__in=bookings,
            full_name__icontains=search,
            
        ).select_related('booking', 'booking__room')
    else:
        guest_details = GuestDetail.objects.filter(
            booking__in=bookings
        ).select_related('booking', 'booking__room')

    

    return render(request, 'manage_guests.html', {
        'hotel': hotel,
        'guests': guest_details,
        'filter_type': filter_type or 'all',
        'booking':booking
    })
def manage_bookings(request,hotel_id):
    hotel=get_object_or_404(Hotel,id=hotel_id)
    booking=Booking.objects.filter(hotel=hotel).select_related('room')
    
    context={
        'hotels':hotel,
        'bookings':booking
    }
    return render(request,'manage_bookings.html',context)


def view_rooms(request,hotel_id,room_id):
    hotel=get_object_or_404(Hotel,id=hotel_id)
    rooms=get_object_or_404(Room,id=room_id,hotel=hotel)

    image_urls = [img.image.url for img in rooms.images.all()]
    
    return render(request, 'view_room.html', {
        'hotel': hotel,
        'room': rooms,
        'image_urls':json.dumps(image_urls),

    })
def hotel_search(request, user_id):
    user = get_object_or_404(userregister, id=user_id)

    # ✅ Annotate each hotel with the minimum price of its rooms
    hotels = Hotel.objects.annotate(min_price=Min('rooms__price_per_night'))

    # ✅ Sorting by dropdown value
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        hotels = hotels.order_by('min_price')
    elif sort == 'price_desc':
        hotels = hotels.order_by('-min_price')

    if request.method == 'POST':
        destination = request.POST.get('destination', '').title()
        check_in = parse_date(request.POST.get('check_in'))
        check_out = parse_date(request.POST.get('check_out'))
        rooms = request.POST.get('rooms')
        adults = request.POST.get('adults')
        children = request.POST.get('children')

        search = HotelSearch.objects.create(
            user=user,
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            rooms=rooms,
            adults=adults,
            children=children
        )
        request.session['latest_search_id'] = search.id
        return redirect('avaliable_hotel', user_id=user.id)

    return render(request, 'hotel_search.html', {
        'user': user,
        'hotels': hotels
    })


def avaliable_hotel(request, user_id):
    user = get_object_or_404(userregister, id=user_id)

    # Get the latest hotel search
    latest_search = HotelSearch.objects.filter(user=user).order_by('-search_date').first()

    # Optional override via session
    search_id = request.session.get('latest_search_id')
    if search_id:
        latest_search = HotelSearch.objects.filter(id=search_id, user=user).first()
        del request.session['latest_search_id']

    hotels = []
    if latest_search:
        destination = latest_search.destination.title()
        # 🧠 Optimize data fetch with related room info and amenities
        hotels = Hotel.objects.filter(city__iexact=destination).prefetch_related(
            'rooms__room_type', 'rooms__amenities'
        )

    return render(request, 'avaliable_hotel.html', {
        'user': user,
        'search': latest_search,
        'hotels': hotels
    })
def select_rooms(request, user_id, hotel_id):
    user = get_object_or_404(userregister, id=user_id)
    hotel = get_object_or_404(Hotel, id=hotel_id)
    rooms = Room.objects.filter(hotel=hotel, status='available').select_related('room_type').prefetch_related('images', 'amenities')
    context = {
        'user': user,
        'hotel': hotel,
        'rooms': rooms
    }
    return render(request, 'select_rooms.html', context)

from .models import Booking,GuestDetail
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt  # For skipping CSRF token in some POSTs (like Razorpay)
from django.http import HttpResponseBadRequest         # To return 400 Bad Request
from datetime import datetime
import razorpay



from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from .models import Booking, Room





def guest_info(request, room_id,user_id):
    room = get_object_or_404(Room, id=room_id)
    user=get_object_or_404(userregister,id=user_id)
    hotel = room.hotel
    total_amount = None  # default before form submit

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')

        # ✅ Convert to date
        check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        # ✅ Calculate total nights
        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            nights = 1  # minimum 1 night

        # ✅ Calculate total amount
        total_amount = room.price_per_night * nights

      

        # ✅ Create Booking
        booking = Booking.objects.create(
            user=user, 
            hotel=hotel, # can be None
            room=room,
            check_in=check_in_date,
            check_out=check_out_date,
            total_amount=total_amount,
            payment_id='',
            payment_status='Pending'
        )

        # ✅ Create GuestDetail
        GuestDetail.objects.create(
            booking=booking,
            hotel=hotel,
            full_name=full_name,
            gender=gender,
            email=email,
            phone=phone,
            address=address
        )

        # ✅ Save booking in session to use in payment view
        request.session['booking_id'] = booking.id

        return redirect('book_room',user_id=user.id,booking_id=booking.id)  # Razorpay payment view

    return render(request, 'guest_info.html', {
        'room': room,
        'total_amount': total_amount
    })


razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def book_room(request,user_id, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user=get_object_or_404(userregister,id=user_id)
    room = booking.room
    amount = int(booking.total_amount * 100)  # Razorpay accepts paise

    razorpay_order = razorpay_client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    context = {
        "room": room,
        "booking": booking,
        "user":user,
        "user_id": user.id, 
        "order_id": razorpay_order['id'],
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "amount": amount,
    }
    return render(request, "hotel_payment.html", context)


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import NewsletterSubscriber




@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            booking_id = request.POST.get('booking_id')
            room_id = request.POST.get('room_id')

            if not (payment_id and booking_id):
                return HttpResponseBadRequest("Missing data.")

            booking = get_object_or_404(Booking, id=booking_id)
            room = get_object_or_404(Room, id=room_id)
            user=booking.user

            booking.payment_id = payment_id
            booking.payment_status = 'Paid'
            booking.status='confirmed'
            booking.save()

            room.status = 'booked'
            room.save()

            print("✅ Payment processed. Redirecting...")

            # ✅ Redirect to success view
            return redirect('payment_success_view', booking_id=booking.id,user_id=user.id)

        except Exception as e:
            import traceback
            traceback.print_exc()
            return HttpResponseBadRequest(f"Error: {str(e)}")

    return HttpResponseBadRequest("Invalid request.")

def payment_success_view(request, booking_id, user_id):
    booking = Booking.objects.get(id=booking_id)
    user = get_object_or_404(userregister, id=user_id)
    room = booking.room

    return render(request, 'success.html', {
        'booking': booking,
        'room': room,
        'user': user
    })
def hotel_my_bookings(request, user_id):
    user = get_object_or_404(userregister, id=user_id)
    today = date.today()
    

    bookings = Booking.objects.filter(user=user).select_related(
        'room__hotel', 'room__room_type'
    ).prefetch_related('room__images', 'room__amenities', 'guest').order_by('-booking_date')

    upcoming = bookings.filter(check_in__gte=today)
    past = bookings.filter(check_out__lt=today)

    return render(request, 'hotel_my_bookings.html', {
        'user': user,
        'upcoming': upcoming,
        'past': past,
    })
@require_POST
def cancel_hotel_bookings(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user = booking.user

    # Mark the booking as cancelled instead of deleting
    booking.status = 'cancelled'

    booking.save()

    # Make the room available again
    if booking.room:
        booking.room.is_booked = False
        booking.room.save()

    messages.success(request, 'Booking cancelled and room is now available.')
    return redirect('hotel_my_bookings', user_id=user.id)
def delete_booking(request, hotel_id, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Ensure the booking belongs to the hotel
    if booking.room.hotel.id == hotel_id:  # assuming Booking → Room → Hotel relation
        room = booking.room
        room.status = 'available'
        room.save()
        booking.delete()
        messages.success(request, "Booking deleted and room marked as available.")
    else:
        messages.error(request, "Unauthorized action.")

    return redirect('hoteldashboard',hotel_id=hotel_id) 




        











    




