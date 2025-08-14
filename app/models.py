from django.db import models
from django.utils import timezone

from owner.models import flight
from django.contrib.auth.models import User

class userregister(models.Model):
    firstname=models.CharField(max_length=50)
    lastname=models.CharField(max_length=50)
    email=models.CharField(unique=True)
    phonenumber=models.CharField(max_length=50)
    address=models.TextField()
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=128)
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

class Flight_search(models.Model):
    departure=models.CharField(max_length=20)
    arrival=models.CharField(max_length=20)
    departure_date=models.DateTimeField()
    return_date=models.DateTimeField(blank=True,null=True)
    passengers=models.PositiveIntegerField()

    def __str__(self):
        return f'{self.departure} to {self.arrival} on {self.departure_date.date()}'
    
class Booking(models.Model):
    user=models.ForeignKey(userregister,on_delete=models.CASCADE)
    flight=models.ForeignKey(flight,on_delete=models.CASCADE)
    passenger=models.PositiveIntegerField()
    selected_seats=models.TextField(blank=True,help_text='comma-seperated  seat codes (e.g. 5A,5B)')
    total_price=models.FloatField(default=0)
    status=models.CharField(max_length=20,choices=[
        ('Confirmed','confirmed'),
        ('Pending','pending'),
        ('Cancelled','cancelled')
    ],default='pending')
    booking_date=models.DateTimeField(auto_now_add=True,blank=True,null=True)

    def __str__(self):
        return f'{self.user}  booked {self.passenger} seats on {self.flight}'
class Review_booking(models.Model):
    user=models.ForeignKey(userregister,on_delete=models.CASCADE)
    flights=models.ForeignKey(flight,on_delete=models.CASCADE)
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE)
    firstname=models.CharField(max_length=50)
    lastname=models.CharField(max_length=50)
    email=models.EmailField(max_length=50)
    phonenumber=models.CharField(max_length=12)
    status = models.CharField(max_length=20, choices=[
        ('Active', 'active'),
        ('Cancelled', 'cancelled')
    ], default='Active')

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.email} {self.phonenumber}'

class PasswordResetLog(models.Model):
    user = models.ForeignKey(userregister, on_delete=models.CASCADE)
    
    ACTION_CHOICES = [
        ('requested', 'Requested'),
        ('completed', 'Completed'),
    ]

    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default='requested')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.action} at {self.timestamp}"
class Refund(models.Model):
    user=models.ForeignKey(userregister,on_delete=models.CASCADE)
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE,related_name='refunds')
    passenger = models.ForeignKey(Review_booking, on_delete=models.CASCADE)
    description=models.TextField()
    status=models.CharField(max_length=20,choices=[
        ('Pending','pending'),
        ('Approved','approved'),
        ('refunded','Refunded'),
        ('Rejected','rejected')
        ],default='pending')
    request_date=models.DateTimeField(default=timezone.now)
    processed_date=models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"Refund for Booking #{self.booking.id} - {self.status}"
class Notification(models.Model):
    recipient=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.TextField()
    refund = models.ForeignKey(Refund, null=True, blank=True, on_delete=models.CASCADE)
    is_read=models.BooleanField(default=False)
    timestamp=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username}"


