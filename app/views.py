from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import userregister,Flight_search,Booking,Review_booking,PasswordResetLog,Refund,Notification
from django.contrib.auth.hashers import make_password,check_password
from datetime import date,datetime
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import never_cache
from owner.models import flight,aircraft,flightowner,Hotel
import requests
from types import SimpleNamespace
from dateutil import parser
from django.http import Http404
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.

def registration(request):
    if request.method=='POST':
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        email=request.POST.get('email')
        phonenumber=request.POST.get('phonenumber')
        address=request.POST.get('address')
        username=request.POST.get('username')
        password=request.POST.get('password')
        confirmpassword=request.POST.get('confirm_password')

        if password!=confirmpassword:
            messages.error(request,'password does not match')
            return redirect('registration')
        if userregister.objects.filter(username=username).exists():
            messages.error(request,'username already exists')
        user=userregister.objects.create(firstname=firstname,lastname=lastname,email=email,phonenumber=phonenumber,address=address,username=username,password=make_password(password))
        user.save()
        messages.success(request,'regustered successfully')
        return redirect('login')
    return render(request,'register.html')

def loginpage(request):
    if 'username' in request.session:
        # Optional: Fetch user ID from DB or session
        user = userregister.objects.get(username=request.session['username'])
        return redirect('user_landing', user_id=user.id)
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        try:
            
            user = userregister.objects.get(username=username)
        except userregister.DoesNotExist:
            messages.error(request, 'Username not found')
            return redirect('login')
        if check_password(password,user.password):
            request.session['username']=user.username
            messages.success(request,'login successfully')
            return redirect('user_landing',user_id=user.id)
        else:
            messages.error(request,'incorrect password')
            return redirect('login')
    return render(request,'login.html')

def landing_page(request):
    return render(request,'landing_page.html')
def feature(request):
    return render(request,'feature.html')
def about(request):
    return render(request,'about.html')

def user_landing(request,user_id):
    user=userregister.objects.get(id=user_id)
    return render(request,'user_landing.html',{'user':user})
def user_profile(request,user_id):
    user=userregister.objects.get(id=user_id)
    return render(request,'userprofile.html',{'user':user})
def edit_profile(request,user_id):
   
    user=userregister.objects.get(id=user_id)
    if request.method=='POST':
        user.firstname=request.POST.get('firstname')
        user.lastname=request.POST.get('lastname')
        user.email=request.POST.get('email')
        user.phonenumber=request.POST.get('phone')
        user.address=request.POST.get('address')
        
        user.save()
        messages.success(request,'updated successfully')
        return redirect('userprofile',user_id=user.id)
    today=date.today()
    
    return render(request,'editprofile.html',{'user':user,'today':today})
@never_cache
def user_logout(request):
    request.session.flush() 
    logout(request)
    return redirect('landing_page')
def flighthome(request,user_id):
    user=userregister.objects.get(id=user_id)
    return render(request,'flighthome.html',{'user':user})


def admin_login(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)
        if user is not None and user.is_staff:
            login(request,user)
            return redirect('admindashboard')
        else:
            messages.error(request,'invalid username and password')
            return redirect('adminlogin')
    return render(request,'adminlogin.html')
def is_admin(user):
    return user.is_authenticated and user.is_staff
@user_passes_test(is_admin, login_url='adminlogin')
def admindashboard(request):
    totalusers=userregister.objects.count()
    totalowners=flightowner.objects.count()
    totalflights=flight.objects.count()
    totalhotels = Hotel.objects.count() 
    today=date.today()
    pending_owners = flightowner.objects.filter(is_approved=False).order_by('-created_at')
    approved_owners = flightowner.objects.filter(is_approved=True).order_by('-created_at')
    unread_count=Notification.objects.filter(recipient=request.user,is_read=False).count()
    return render(request, 'admindashboard.html',{'total_users':totalusers,'total_owners':totalowners,'total_flights':totalflights,'total_hotels':totalhotels,'today':today,'pending_owners': pending_owners,'approved_owners': approved_owners,'unread_count':unread_count})
def approve_owner(request,owner_id):
    owner=get_object_or_404(flightowner,id=owner_id)
    owner.is_approved=True
    owner.save()
    send_mail(
        subject='Owner Approval - AeroTrack',
        message=f'Hello {owner.fullname},\n\nYour flight owner account has been approved. You may now log in and access your dashboard.\n\nThanks,\nAdmin',
        from_email='firoznissar@gmail.com',  # Replace with your SMTP sender
        recipient_list=[owner.email],       # Automatically fetched from DB
        fail_silently=False,
    )
    messages.info(request, f'{owner.fullname} got a mail successfully ')
    return redirect('admindashboard')
def adminlogout(request):
    
    return redirect('landing_page')

def flight_search(request, user_id):
    user = userregister.objects.get(id=user_id)
    searchingflight = None
    real_flights=[]

    if request.method == 'POST':
        departure = request.POST.get('source')
        arrival = request.POST.get('destination')
        departure_date = request.POST.get('departure_date')
        return_date = request.POST.get('return_date')
        passengers = request.POST.get('passengers')
        print("Departure:", departure)
        print("Arrival:", arrival)
        print("Departure Date:", departure_date)
        print("Passengers:", passengers)


        try:
            departure_date_obj = datetime.strptime(departure_date, '%Y-%m-%d')
        except ValueError:
            messages.error(request, 'Invalid departure date format.')
            return redirect('flighthome', user_id=user.id)

        return_date_obj = None
        if return_date:
            try:
                return_date_obj = datetime.strptime(return_date, '%Y-%m-%d')
            except ValueError:
                messages.error(request, 'Invalid return date format.')
                return redirect('flighthome', user_id=user.id)

        # Save the search query
        Flight_search.objects.create(
            departure=departure,
            arrival=arrival,
            departure_date=departure_date,
            return_date=return_date_obj,
            passengers=int(passengers)
        )

        passenger_count = int(passengers)

        # Filter matching flights
        searchingflight = flight.objects.filter(
            departure_airport__icontains=departure,
            arrival_airport__icontains=arrival,
            departure_time__date=departure_date_obj.date(),
            status__iexact='scheduled',
            aircraft_type__seat_capacity__gte=passenger_count
        )

        # Add total prices for each flight
        for f in searchingflight:
            f.economy_per_ticket = f.economy_class_price
            f.business_per_ticket = f.business_class_price
            f.total_economy_price = f.economy_class_price * passenger_count
            f.total_business_price = f.business_class_price * passenger_count
        try:
            api_key='f0b8eaf90b0b5324f6678f990ea85987'
            api_url='http://api.aviationstack.com/v1/flights'
            city_to_iata = {
                'delhi': 'DEL',
                'mumbai': 'BOM',
                'bangalore': 'BLR',
                'kolkata': 'CCU',
                'chennai': 'MAA',
                'trivandrum': 'TRV',
                'hyderabad': 'HYD',
                'ahmedabad': 'AMD',
                'pune': 'PNQ',
                'jaipur': 'JAI',
                'goa': 'GOI',
                'kochi': 'COK',
                'lucknow': 'LKO',
                'bhubaneswar': 'BBI',
                'coimbatore': 'CJB',
                'nagpur': 'NAG',
                'indore': 'IDR',
                'visakhapatnam': 'VTZ',
                'patna': 'PAT',
                'guwahati': 'GAU',
                'ranchi': 'IXR',
                'amritsar': 'ATQ',
                'srinagar': 'SXR',
                'dehradun': 'DED',
                'madurai': 'IXM',
                'varanasi': 'VNS',
                'raipur': 'RPR',
                'aurangabad': 'IXU',
                'trichy': 'TRZ',
                'vadodara': 'BDQ'
            }


            dep_code = city_to_iata.get(departure.lower())
            arr_code = city_to_iata.get(arrival.lower())

            params={
                'access_key': api_key,
                'limit':10 ,
                'dep_iata':dep_code,
                'arr_iata':arr_code               

            }
            response=requests.get(api_url,params=params)
            print("API URL:", response.url)
            print("Status Code:", response.status_code)
            print("API Response:", response.text)

            real_data = response.json()
            real_flights = real_data.get('data', [])
            # Airline logos dictionary
            
            airline_logos = {
                   'IndiGo': 'logos/indigo.png',
                   'Air India': 'logos/airindia.png'
                    
                # Replace others similarly with PNGs if SVGs fail
            }

            

            

            for flight_data in real_flights:
                airline_name = flight_data['airline'].get('name') or 'Unknown Airline'
                flight_data['airline']['name'] = airline_name
                flight_data['airline']['logo'] = airline_logos.get(airline_name.strip())
                print(f"Matched airline: {airline_name}, Logo: {flight_data['airline']['logo']}")


                flight_data['flight']['iata'] = flight_data['flight'].get('iata') or 'N/A'
                flight_data['departure']['airport'] = flight_data['departure'].get('airport') or 'Unknown Departure'
                flight_data['arrival']['airport'] = flight_data['arrival'].get('airport') or 'Unknown Arrival'

                # Scheduled datetime parsing
                dep_time_str = flight_data['departure'].get('scheduled') or flight_data['departure'].get('estimated')
                arr_time_str = flight_data['arrival'].get('scheduled') or flight_data['arrival'].get('estimated')

                try:
                    flight_data['departure']['scheduled'] = parser.parse(dep_time_str) if dep_time_str else None
                except Exception:
                    flight_data['departure']['scheduled'] = None

                try:
                    flight_data['arrival']['scheduled'] = parser.parse(arr_time_str) if arr_time_str else None
                except Exception:
                    flight_data['arrival']['scheduled'] = None


            def dict_to_namespace(d):
                for k, v in d.items():
                    if isinstance(v, dict):
                        d[k] = dict_to_namespace(v)
                return SimpleNamespace(**d)

            real_flights = [dict_to_namespace(f) for f in real_flights]
            

            for rf in real_flights:
                print(f"Flight: {rf.flight.iata}, From: {rf.departure.airport}, To: {rf.arrival.airport}")


        except Exception as e:
            print(f'api_error:{e}')
            messages.warning(request,'real time flight cant be loaded')

        messages.success(request, 'Available flights based on your search:')
        return render(request, 'flighthome.html', {
            'user': user,
            'flights': searchingflight,
            'real_flights':real_flights,
            'searched_passengers': passenger_count
        })
    


    return render(request, 'flighthome.html', {
        'user':user ,
        'flights': [],
        'real_flights': [],
        'searched_passengers': 1})


def generate_seat(aircraft_id):
    aircrafts=aircraft.objects.get(id=aircraft_id)
    seat_capacity=int(aircrafts.seat_capacity)
    layout={
        'aircrafts':aircrafts,
        'business':[],
        'economy':[],
        'config':''
    }
    if seat_capacity<=80:
        seats_per_row = 4
        seat_labels = ['A', 'B', 'C', 'D']
        rows = (seat_capacity + seats_per_row - 1) // seats_per_row
        layout['config'] = '2-2'

        for row in range(1, rows + 1):
            layout['economy'].append([f"{row}{label}" for label in seat_labels])
    elif seat_capacity<=180:
        seats_per_row = 6
        seat_labels = ['A', 'B', 'C', 'D', 'E', 'F']
        rows = (seat_capacity + seats_per_row - 1) // seats_per_row
        layout['config'] = '3-3'

        for row in range(1, rows + 1):
            layout['economy'].append([f"{row}{label}" for label in seat_labels])
    else:
        # Large aircraft: 10 seats/row (3-4-3)
        seats_per_row = 10
        seat_labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K']
        rows = (seat_capacity + seats_per_row - 1) // seats_per_row
        layout['config'] = '3-4-3'

        # Optional: first 20% as Business (2-2-2, 6 seats per row)
        business_rows = min(6, rows // 5)
        business_labels = ['A', 'B', 'C', 'D', 'E', 'F']

        for row in range(1, business_rows + 1):
            layout['business'].append([f"{row}{label}" for label in business_labels])

        # Remaining rows as Economy
        start_row = business_rows + 1
        for row in range(start_row, rows + 1):
            layout['economy'].append([f"{row}{label}" for label in seat_labels])

    return layout
def seats_view(request, user_id, flight_id, aircraft_id):
    user = userregister.objects.get(id=user_id)
    flights = flight.objects.get(id=flight_id)
    layout = generate_seat(aircraft_id)

    # ✅ Collect already booked seats
    booked = Booking.objects.filter(flight=flights).values_list('selected_seats', flat=True)
    booked_seats = set()
    for seats in booked:
        if seats:
            booked_seats.update(seat.strip().upper() for seat in seats.split(','))

    context = {
        'user': user,
        'flights': flights,
        'aircraft': ['aircraft'],
        'business': layout.get('business', []),
        'economy': layout.get('economy', []),
        'config': layout.get('config', ''),
        'booked_seats': booked_seats  # ✅ Send to template
    }
    return render(request, 'seating_layout.html', context)


def booking_flight(request, user_id, flight_id):
    user = userregister.objects.get(id=user_id)
    flight_obj = flight.objects.get(id=flight_id)

    booking_id = request.GET.get('booking_id')
    existing_passengers = []
    booking = None

    if booking_id:
        try:
            booking = Booking.objects.get(id=booking_id)
            existing_passengers = Review_booking.objects.filter(booking=booking)
            selected_seats = booking.selected_seats
            cleaned_seats = selected_seats.split(",") if selected_seats else []
        except Booking.DoesNotExist:
            booking = None
            cleaned_seats = []
    else:
        cleaned_seats = []

    if request.method == 'POST':
        selected_seats = request.POST.get('selected_seats', '')
        raw_selected_seats = selected_seats.split(',')
        cleaned_seats = [seat.strip().upper() for seat in raw_selected_seats if seat.strip()]
        status = request.POST.get('status')

        aircraft_id = flight_obj.aircraft_type.id
        layout = generate_seat(aircraft_id)

        business_seats = {seat.upper() for row in layout.get('business', []) for seat in row}
        economy_seats = {seat.upper() for row in layout.get('economy', []) for seat in row}

        business_count = sum(1 for seat in cleaned_seats if seat in business_seats)
        economy_count = sum(1 for seat in cleaned_seats if seat in economy_seats or seat not in business_seats)

        business_price = float(flight_obj.business_class_price) * business_count
        economy_price = float(flight_obj.economy_class_price) * economy_count
        base_price = business_price + economy_price
        tax_percentage = float(flight_obj.tax_percentage or 0)
        tax_amount = base_price * (tax_percentage / 100)
        total_price = base_price + tax_amount

        # Check for seat conflict
        already_booked = Booking.objects.filter(flight=flight_obj).exclude(id=booking.id if booking else None).values_list('selected_seats', flat=True)
        booked_seats_set = set()
        for s in already_booked:
            if s:
                booked_seats_set.update([x.strip().upper() for x in s.split(',')])

        conflict = set(cleaned_seats) & booked_seats_set
        if conflict:
            return render(request, 'bookingflight.html', {
                'user': user,
                'flights': flight_obj,
                'error': f"Seats already booked: {', '.join(conflict)}. Please choose other seats.",
                'existing_passengers': existing_passengers,
                'booking': booking,
                'searched_passengers': len(cleaned_seats),
                'selected_seats': ','.join(cleaned_seats)
            })

        # Save the booking (new or update)
        if booking:
            booking.selected_seats = ','.join(cleaned_seats)
            booking.passenger = len(cleaned_seats)
            booking.total_price = total_price
            booking.save()
            Review_booking.objects.filter(booking=booking).delete()
        else:
            booking = Booking.objects.create(
                user=user,
                flight=flight_obj,
                passenger=len(cleaned_seats),
                selected_seats=','.join(cleaned_seats),
                total_price=total_price,
                status='pending'
            )
            booking.save()

        # 🔥 Always send updated booking object
        context = {
            'user': user,
            'flights': flight_obj,
            'booking': booking,
            'searched_passengers': len(cleaned_seats),
            'selected_seats': ','.join(cleaned_seats),
            'business_count': business_count,
            'economy_count': economy_count,
            'business_price': business_price,
            'economy_price': economy_price,
            'base_price': base_price,
            'tax_amount': tax_amount,
            'total_price': total_price,
            'status': 'pending',
            'existing_passengers': existing_passengers,
        }

        return render(request, 'bookingflight.html', context)

    # For GET method
    return render(request, 'bookingflight.html', {
        'user': user,
        'flights': flight_obj,
        'existing_passengers': existing_passengers,
        'booking': booking,
        'searched_passengers': len(cleaned_seats),
        'selected_seats': ','.join(cleaned_seats)
    })


def review_booking(request,user_id,flight_id,booking_id):
    
    user=userregister.objects.get(id=user_id)
    flights=flight.objects.get(id=flight_id)
    booking=Booking.objects.get(id=booking_id)
    if request.method=='POST':
        searched_passengers=int(request.POST.get('searched_passengers'))
        for i in range(1,searched_passengers+1):
            firstname=request.POST.get(f'first_name_{i}')
            lastname=request.POST.get(f'last_name_{i}')
            email=request.POST.get(f'email_{i}')
            phonenumber=request.POST.get(f'phone_{i}')
            Review_booking.objects.create(
                user=user,
                flights=flights,
                booking=booking,
                firstname=firstname,
                lastname=lastname,
                email=email,
                phonenumber=phonenumber
            )

        
        
            
        return redirect('booking_summary',user_id=user.id,flight_id=flights.id,booking_id=booking.id)
    
    return render(request,'bookflight.html',{
        'user':user,
        'flights':flights,
        'booking':booking,
        'searched_passengers':searched_passengers})
import itertools # We'll use this for the seat assignment


# Assuming your models are imported correctly from your app's models.py
# from .models import userregister, flight, Booking, Review_booking

def ticket_generate(request, user_id, flight_id, booking_id):
    """
    Generates a page displaying individual boarding passes for each passenger
    associated with a specific booking. Seat numbers are dynamically assigned
    from the booking's selected_seats field for display purposes.
    """
    try:
        user = userregister.objects.get(id=user_id)
        flights = flight.objects.get(id=flight_id)
        booking = Booking.objects.get(id=booking_id)
    except (userregister.DoesNotExist, flight.DoesNotExist, Booking.DoesNotExist):
        messages.error(request, "Invalid user, flight, or booking details provided.")
        # Redirect to a safe page if critical objects are not found
        return redirect('some_error_or_home_page') # Replace with your actual URL name

    # Fetch all Review_booking instances related to this specific booking.
    # It's crucial to order them consistently so that seats are assigned
    # in the same order every time the page is loaded.
    # 'id' or 'created_at' are good candidates for consistent ordering.
    passengers_queryset = Review_booking.objects.filter(
        user=user,
        flights=flights,
        booking=booking,
        status='Active'  # ✅ Only show active passengers
    ).order_by('id')

    if not passengers_queryset.exists():
        messages.info(request, "This ticket has been cancelled or no active passengers remain.")
        return redirect('user_landing', user_id=user.id)


    if not passengers_queryset.exists():
        messages.info(request, "No passenger details found for this booking. Please ensure passenger details were entered.")
        # Redirect the user if there are no passengers to display tickets for
        return redirect('user_landing',user_id=user.id) # Replace with your actual URL name

    # Get the list of all selected seats from the Booking object.
    # booking.selected_seats is a TextField (e.g., 'A1,B2,C3').
    # We split it into a list of individual seat strings.
    all_selected_seats = [seat.strip().upper() for seat in booking.selected_seats.split(',') if seat.strip()]

    # Create an iterator for the list of seats.
    # An iterator allows us to consume seats one by one using next().
    seat_iterator = itertools.cycle(all_selected_seats) # Using itertools.cycle to repeat seats if more passengers than seats

    # Prepare a new list that will hold enhanced passenger data for the template.
    # Each item will be a dictionary containing original Review_booking fields
    # plus a 'seat_number' assigned dynamically.
    assigned_passengers_for_template = []

    for passenger_obj in passengers_queryset:
        # Get the next seat from the iterator.
        # If all_selected_seats is empty, current_passenger_seat will be None.
        # If there are more passengers than unique seats, itertools.cycle will
        # loop back and assign seats again (e.g., 4 passengers, 3 seats -> A1, B2, C3, A1).
        current_passenger_seat = next(seat_iterator, None)

        # Construct a dictionary for each passenger.
        # We copy all fields from the Review_booking instance and add 'seat_number'.
        temp_passenger_data = {
            'id': passenger_obj.id,
            'firstname': passenger_obj.firstname,
            'lastname': passenger_obj.lastname,
            'email': passenger_obj.email,
            'phonenumber': passenger_obj.phonenumber,
            'created_at': passenger_obj.created_at,
            'updated_at': passenger_obj.updated_at,
            'seat_number': current_passenger_seat, # <-- The dynamically assigned seat for display
        }
        assigned_passengers_for_template.append(temp_passenger_data)

    context = {
        'user': user,
        'flights': flights,
        'booking': booking,
        'passengers': assigned_passengers_for_template, # Pass this list to your template
    }
    return render(request, 'ticket_generate.html', context)
import razorpay
from django.conf import settings

def booking_summary(request, user_id, flight_id, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    user = get_object_or_404(userregister, id=user_id)
    selected_flight = get_object_or_404(flight, id=flight_id)
    passengers = Review_booking.objects.filter(booking=booking)

    selected_seats = booking.selected_seats.split(",") if booking.selected_seats else []
    passengers_with_seats = []

    for index, passenger in enumerate(passengers):
        seat = selected_seats[index] if index < len(selected_seats) else "N/A"
        passengers_with_seats.append({
            'data': passenger,
            'seat': seat
        })

    base_price = booking.total_price
    tax_percent = 15
    tax_amount = base_price * (tax_percent / 100)
    total_amount = base_price + tax_amount

    # Razorpay integration
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    amount_paise = int(total_amount * 100)  # Razorpay requires paise
    payment = client.order.create({
        "amount": amount_paise,
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        'booking': booking,
        'flight': selected_flight,
        'passengers_with_seats': passengers_with_seats,
        'base_price': base_price,
        'tax_percent': tax_percent,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
        'user': user,
        'razorpay_order_id': payment['id'],
        'razorpay_key': settings.RAZORPAY_KEY_ID,
        'amount': amount_paise
    }

    return render(request, 'booking_summary.html', context)

def edit_passenger(request,passenger_id):
    passenger=get_object_or_404(Review_booking,id=passenger_id)
    if request.method=='POST':
        passenger.firstname=request.POST.get('username')
        passenger.lastname=request.POST.get('lastname')
        passenger.email=request.POST.get('email')
        passenger.phonenumber=request.POST.get('phone')
        passenger.save()
        messages.success(request,'passenger details updated successfully')
        return redirect('booking_summary',passenger.booking.user.id,passenger.booking.flight.id,passenger.booking.id)
    return render(request,'edit_passenger.html',{'passenger':passenger})
 # Razorpay sends POST without CSRF token
def payment_success(request, booking_id):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        booking = get_object_or_404(Booking, id=booking_id)
        user = booking.user
        flights = booking.flight

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            booking.payment_status = "confirmed"
            booking.status='confirmed'
            booking.razorpay_order_id = razorpay_order_id
            booking.save()
            messages.success(request, 'Ticket is ready for onboarding.')

            # Fetch and assign passengers with seat numbers
            passengers_queryset = Review_booking.objects.filter(
                user=user, flights=flights, booking=booking
            ).order_by('id')

            all_selected_seats = [seat.strip().upper() for seat in booking.selected_seats.split(',') if seat.strip()]
            seat_iterator = itertools.cycle(all_selected_seats)

            assigned_passengers = []
            for passenger_obj in passengers_queryset:
                seat = next(seat_iterator, None)
                assigned_passengers.append({
                    'id': passenger_obj.id,
                    'firstname': passenger_obj.firstname,
                    'lastname': passenger_obj.lastname,
                    'email': passenger_obj.email,
                    'phonenumber': passenger_obj.phonenumber,
                    'created_at': passenger_obj.created_at,
                    'updated_at': passenger_obj.updated_at,
                    'seat_number': seat,
                })

            return render(request, 'ticket_generate.html', {
                'booking': booking,
                'user': user,
                'flights': flights,
                'passengers': assigned_passengers,
                'payment_id': razorpay_payment_id,
            })

        except razorpay.errors.SignatureVerificationError:
            return render(request, 'payment_failed.html', {
                'booking': booking,
                'error': "Signature verification failed. Payment not confirmed."
            })

    return render(request, 'payment_failed.html', {
        'error': "Invalid request method. Payment failed."
    })
def cancel_passenger_ticket(request, passenger_id):
    passenger = get_object_or_404(Review_booking, id=passenger_id)
    booking = passenger.booking
    user = passenger.user

    if passenger.status == 'Cancelled':
        messages.warning(request, "This passenger is already cancelled.")
        return redirect('my_bookings', user.id)

    # Mark as cancelled
    booking.status = 'confirmed'
    booking.save()

    # Reduce passenger count in Booking
    booking.passenger = max(booking.passenger - 1, 0)
    booking.save()

    # If no active passengers left, delete the booking
    if not Review_booking.objects.filter(booking=booking, status='Active').exists():
        booking.delete()
        messages.info(request, "All passengers cancelled. Booking deleted.")
        return redirect('my_bookings', user.id)

    messages.success(request, "Passenger ticket cancelled successfully.")
    return redirect('my_bookings', user.id)



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def generate_ticket_pdf(request, user_id, flight_id, booking_id):
    user = get_object_or_404(userregister, id=user_id)
    flight_obj = get_object_or_404(flight, id=flight_id)
    booking = get_object_or_404(Booking, id=booking_id)

    passengers_queryset = Review_booking.objects.filter(
        user=user,
        flights=flight_obj,
        booking=booking,
        status='Active'
    ).order_by('id')

    # Parse seats
    seats = [seat.strip().upper() for seat in booking.selected_seats.split(',') if seat.strip()]

    # Check for mismatch
    if len(seats) != passengers_queryset.count():
        return HttpResponse("Seat count doesn't match passenger count.")

    # Assign each seat to a passenger one-to-one
    assigned_passengers = []
    for passenger_obj, seat in zip(passengers_queryset, seats):
        assigned_passengers.append({
            'id': passenger_obj.id,
            'firstname': passenger_obj.firstname,
            'lastname': passenger_obj.lastname,
            'email': passenger_obj.email,
            'phonenumber': passenger_obj.phonenumber,
            'created_at': passenger_obj.created_at,
            'updated_at': passenger_obj.updated_at,
            'seat_number': seat,
        })

    context = {
        'user': user,
        'flights': flight_obj,
        'booking': booking,
        'passengers': assigned_passengers,
    }

    # Render and generate PDF
    template_path = 'ticket_generate.html'  # make sure this exists and is PDF-safe
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="boarding_pass_{booking.id}.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response
def my_bookings(request, user_id):
    user = get_object_or_404(userregister, id=user_id)
    bookings = Booking.objects.filter(user=user)

    booking_with_passengers = []

    for booking in bookings:
        all_passengers = Review_booking.objects.filter(user=user, booking=booking)
        active_passengers = all_passengers.filter(status='Active')

        if not active_passengers.exists():
            # ✅ Delete only if no Active passengers are left
            booking.delete()
            continue

        booking.display_status = 'Confirmed'  # Optional: you can add logic for full 'Cancelled' if needed
        booking_with_passengers.append((booking, active_passengers))  # ✅ Only include Active passengers

    return render(request, 'my_bookings.html', {
        'booking_with_passengers': booking_with_passengers,
        'user': user
    })



from django.db.models import Q

def manage_user(request):
    user=userregister.objects.all().order_by('-id')
    if request.method=='POST':
        search=request.POST.get('search')
        
        if search:
            user=user.filter(
                Q(firstname__icontains=search) |
                Q(username__icontains=search)
            )
    return render(request,'manage_user.html',{'user':user})
def delete_user(request,user_id):
    user=get_object_or_404(userregister,id=user_id)
    user.delete()
    return redirect('manage_user')
def manage_owner(request):
    owners=flightowner.objects.all().order_by('-id')
    if request.method=='POST':
        search=request.POST.get('search')
        if search:
            owners=flightowner.objects.filter(
            Q(fullname__icontains=search) |
            Q(email__icontains=search)
            )
    return render(request,'manage_owners.html',{'owners':owners})
def delete_owner(request, owner_id):
    try:
        owner = flightowner.objects.get(id=owner_id)

        # Delete all flights linked to the owner (this will also delete related bookings if set to cascade)
        
       
        # Now delete the owner
        owner.delete()

        messages.success(request, "Flight owner and related flights deleted successfully.")
    except flightowner.DoesNotExist:
        messages.error(request, "Flight owner not found.")
    return redirect('manage_owner')
def manage_flights(request):
    flights=flight.objects.all().order_by('-id')
    if request.method=='POST':
        search=request.POST.get('search')
        if search:
            flights=flight.objects.filter(
                Q(aircraft_type__icontains=search)  |
                Q(aircraft_type__owner__companyname__icontains=search)
            )
    return render(request,'manage_flights.html',{'flights':flights})
def delete_flight(request, flight_id):
    if request.method == 'POST':
        flights = get_object_or_404(flight, id=flight_id)

        

        # Delete the flight
        flights.delete()

        messages.success(request, "Flight and related bookings deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('manage_flights')

#user forget password resetting

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class CustomUserTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email}"
        
token_generator = CustomUserTokenGenerator()


from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str





# Use your custom token generator
token_generator = CustomUserTokenGenerator()

def forget_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = userregister.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = token_generator.make_token(user)
            reset_link = request.build_absolute_uri(f'/reset_password/{uid}/{token}/')

            send_mail(
                subject='AeroTrack Password Reset',
                message=f'Hi {user.username},\n\nClick the link below to reset your password:\n{reset_link}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            PasswordResetLog.objects.create(user=user, action='requested', ip_address=request.META.get('REMOTE_ADDR'))

            messages.success(request, 'Reset link has been sent to your email.')
            return redirect('forgot_password')

        except userregister.DoesNotExist:
            messages.error(request, 'Email not found.')
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = userregister.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, userregister.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            
            # ✅ Securely hash the new password
            user.password = make_password(new_password)
            user.save()

            # Log the reset
            PasswordResetLog.objects.create(user=user, action='completed', ip_address=request.META.get('REMOTE_ADDR'))

            messages.success(request, 'Password reset successful. You can now log in.')
            return redirect('login')

        return render(request, 'reset_password.html', {'validlink': True})
    else:
        return render(request, 'reset_password.html', {'validlink': False})
    
    

from django.utils import timezone
from django.contrib.auth.models import User

def refund_policy(request, user_id, booking_id, passenger_id):  # include passenger_id too
    user = get_object_or_404(userregister, id=user_id)
    booking = get_object_or_404(Booking, id=booking_id)
    passenger = get_object_or_404(Review_booking, id=passenger_id, booking=booking)

    if request.method == 'POST':
        description = request.POST.get('description')

        if description:
            # ✅ Create refund request
            refund = Refund.objects.create(
                user=user,
                booking=booking,
                passenger=passenger,
                description=description,
                status='Pending',
                request_date=timezone.now()
            )

            # ✅ Notify all admin users
            admin_users = User.objects.filter(is_staff=True)
            for admin in admin_users:
                Notification.objects.create(
                    recipient=admin,
                    message=f"Refund request from {user.username} for {passenger.firstname} (Booking #{booking.id})",
                    refund=refund
                )

            messages.success(request, 'Refund request sent successfully. Wait for admin approval.')
            return redirect('my_bookings', user_id=user.id)

        else:
            messages.error(request, 'Please enter a reason for refund.')


    return render(request, 'refund_policy.html', {'user': user, 'booking': booking})
@user_passes_test(is_admin, login_url='adminlogin')
def admin_notification(request):
    print("ADMIN LOGGED IN:", request.user)
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    print("NOTIFICATIONS FETCHED:", notifications)
    return render(request, 'admin_notification.html', {'notifications': notifications})
def admin_refund_request(request, refund_id):
    refund = get_object_or_404(Refund, id=refund_id)
    passenger=refund.passenger
    # Mark notification as read if it exists and is unread
    Notification.objects.filter(refund=refund, is_read=False).update(is_read=True)

    return render(request, 'admin_refund_view.html', {'refund': refund,'passenger':passenger})


from django.utils.timezone import now


def update_refund_request(request, refund_id, passenger_id):
    refund = get_object_or_404(Refund, id=refund_id)
    passenger = get_object_or_404(Review_booking, id=passenger_id)

    status = request.POST.get('status')  # 'approved' or 'rejected'

    if status not in ['approved', 'rejected']:
        messages.error(request, 'Invalid status.')
        return redirect('admin_refund_view')

    # ✅ Update refund status
    refund.status = status
    refund.processed_date = now()
    refund.save()

    # ✅ If approved, cancel only the passenger
    if status == 'approved':
        passenger.status = 'Cancelled'
        passenger.save()

    # ✅ Send email to the passenger only
    send_mail(
        subject=f"Refund {status.capitalize()}",
        message=f"Hi {passenger.firstname},\n\nYour refund for Booking #{refund.booking.id} has been {status}.it will be refunded within 5 days.thank you for the interest in aerotrack.",
        from_email='firoznissar@gmail.com',
        recipient_list=[passenger.email],  # ✅ Only that passenger's email
        fail_silently=False,
    )

    messages.success(request, f'Refund has been {status} and email sent to passenger.')
    return redirect('admindashboard')
def manage_hotels(request):
    hotels=Hotel.objects.all().order_by('-id')
    if request.method=='POST':
        search=request.POST.get('search')
        if search:
            hotels=Hotel.objects.filter(
                Q(hotel_name__icontains=search)  |
                Q(city__icontains=search)
            )
    return render(request,'manage_hotels.html',{'hotel':hotels})
def delete_hotels(request,hotel_id):
    hotels=get_object_or_404(Hotel,id=hotel_id)
    hotels.delete()
    return redirect('manage_hotels')








    



    
