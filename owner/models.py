from django.db import models

# Create your models here.
class flightowner(models.Model):

    #Account Details
    fullname=models.CharField(max_length=20)
    email=models.EmailField(max_length=50)
    phonenumber=models.CharField(max_length=15)
    password=models.CharField(max_length=128)

    #Bussiness Information
    Companyname=models.CharField(max_length=100)
    bussiness_registration_number=models.CharField(max_length=20)
    license_number=models.CharField(max_length=50)
    years_of_operation=models.PositiveIntegerField()

    #Address Details
    address=models.TextField()
    city=models.CharField(max_length=20)
    state=models.CharField(max_length=50)
    postal_code=models.CharField(max_length=20)
    country=models.CharField(max_length=50)

    #Flight service details
    number_of_aircrafts=models.PositiveIntegerField()
    FLIGHT_TYPE=[
        ('domestic','Domestic'),
        ('international','International'),
        ('cargo','Cargo'),
        ('charter','Charter')
    ]
    flight_type=models.CharField(max_length=50,choices=FLIGHT_TYPE)
    airline_code=models.PositiveIntegerField(blank=True,null=True)

    #upload documents
    airline_license = models.FileField(upload_to='documents/licenses/')
    registration_certificate = models.FileField(upload_to='documents/certificates/')
    government_id_proof = models.FileField(upload_to='documents/id_proofs/')

    #agreement
    agree_terms=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    #approvement
    is_approved = models.BooleanField(default=False)

    


class Hotel(models.Model):
    hotel_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=10)
    registration_number = models.CharField(max_length=100)
    license_number = models.CharField(max_length=100)
    total_rooms = models.PositiveIntegerField()
    password = models.CharField(max_length=128)  
    image = models.ImageField(upload_to='hotel_images/image/', null=True, blank=True)


class aircraft(models.Model):
    owner=models.ForeignKey(flightowner,on_delete=models.CASCADE,related_name='aircrafts')
    manufacturer=models.CharField(max_length=20)
    model=models.CharField(max_length=20)
    registation_number=models.CharField(max_length=20)
    seat_capacity=models.PositiveIntegerField()
    aircraft_image=models.ImageField(upload_to='aircrafts/',blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.manufacturer} {self.model} ({self.registation_number})'

    
class flight(models.Model):
    flight_number=models.CharField(max_length=20,unique=True)
    aircraft_type=models.ForeignKey(aircraft,on_delete=models.CASCADE)
    departure_airport=models.CharField(max_length=100)
    arrival_airport=models.CharField(max_length=100)
    departure_time=models.DateTimeField()
    arrival_time=models.DateTimeField()
    business_class_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    economy_class_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, help_text='Enter tax as percentage e.g. 18.00 for 18%')

    duration=models.CharField(max_length=50)
    status=models.CharField(max_length=20,choices=[
        ('scheduled','Scheduled'),
        ('delayed','Delayed'),
        ('cancelled','cancelled'),
        ('landed','Landed'),
        

    ],default='scheduled')
    baggage_allowance=models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.flight_number}'
    
class HotelBooking(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()  # 👈 Add this
    checkin_date = models.DateField()
    checkout_date = models.DateField()
    guests = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)



class RoomType(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name



class Room(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('booked', 'Booked'),
        ('unavailable', 'Unavailable'),
    ]
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE, related_name='rooms')
    room_type = models.ForeignKey(RoomType, on_delete=models.SET_NULL, null=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return f"{self.hotel.hotel_name} - Room {self.id}"


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='room_images/')

    def __str__(self):
        return f"Image for {self.room}"



class RoomFacility(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='amenities')
    name = models.CharField(max_length=100)  # e.g., "Free WiFi", "TV", "AC"

    def __str__(self):
        return f"{self.room} - {self.name}"
class HotelSearch(models.Model):
    user = models.ForeignKey('app.userregister', on_delete=models.CASCADE, null=True, blank=True)
    destination = models.CharField(max_length=50)
    check_in = models.DateField()
    check_out = models.DateField()
    rooms = models.IntegerField(default=1)
    adults = models.IntegerField(default=1)
    children = models.IntegerField(default=0)
    search_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.destination} ({self.check_in} to {self.check_out})"
    
class Booking(models.Model):
    user = models.ForeignKey('app.userregister', on_delete=models.CASCADE,related_name='app_bookings',null=True,blank=True)  # or userregister if you're using a custom model
    hotel=models.ForeignKey('Hotel',on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100)
    payment_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    ], default='Pending')
    status=models.CharField(max_length=20,choices=[
        ('confirmed',"Confirmed"),
        ('cancelled','Cancelled'),
        ('pending','Pending')
    ],default='pending')

    def __str__(self):
        return f"Booking by {self.user.username if self.user else 'Guest'} - Room {self.room.id} - ₹{self.total_amount}"

class GuestDetail(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='guest')
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)  # 🔗 Add this line
    full_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=[
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ])
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - Booking #{self.booking.id}"
    
class NewsletterSubscriber(models.Model):
    email=models.EmailField(unique=True)
    subscribed_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email




    

