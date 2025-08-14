
from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('',views.landing_page,name='landing_page'),
    path('registration/',views.registration,name='register'),
    path('login/',views.loginpage,name='login'),
    path('feature/',views.feature,name='feature'),
    path('about/',views.about,name='about'),
    path('user_landing/<int:user_id>/',views.user_landing,name='user_landing'),
    path('user_profile/<int:user_id>/',views.user_profile,name='userprofile'),
    path('edit_profile/<int:user_id>/',views.edit_profile,name='editprofile'),
    path('flighthome/<int:user_id>/',views.flighthome,name='flighthome'),
    path('user_logout/',views.user_logout,name='user_logout'),



    #adminlogin

    path('admin/', admin.site.urls),
    path('adminlogin/',views.admin_login,name='adminlogin'),
    path('admindashboard/',views.admindashboard,name='admindashboard'),
    path('logout/',views.adminlogout,name='adminlogout'),
    path('manage_user/',views.manage_user,name='manage_user'),
    path('delete_user/<int:user_id>/',views.delete_user,name='delete_user'),
    path('manage_owner/',views.manage_owner,name='manage_owner'),
    path('delete_owner/<int:owner_id>/',views.delete_owner,name='delete_owner'),
    path('manage_flights/',views.manage_flights,name='manage_flights'),
    path('delete_flights/<int:flight_id>/',views.delete_flight,name='delete_flight'),
    path('approve_owner/<int:owner_id>/',views.approve_owner,name='approve_owner'),
    path('admin_notification/',views.admin_notification,name='admin_notification'),
    path('admin_refund_view/<int:refund_id>/',views.admin_refund_request,name='admin_refund_view'),
    path('update_refund_request/<int:refund_id>/<int:passenger_id>/',views.update_refund_request,name='update_refund_request'),
    path('manage_hotels/',views.manage_hotels,name='manage_hotels'),
    path('delete_hotels/<int:hotel_id>/',views.delete_hotels,name='delete_hotels'),

    #flightbooking
    path('flight_search/<int:user_id>/',views.flight_search,name='flighthome'),
    path('seats_view/<int:user_id>/<int:flight_id>/<int:aircraft_id>/',views.seats_view,name='seating_layout'),
    path('booking_flight/<int:user_id>/<int:flight_id>/',views.booking_flight,name='bookingflight'),
    path('review_booking/<int:user_id>/<int:flight_id>/<int:booking_id>/',views.review_booking,name='review_booking'),
   
    path('ticket_generate/<int:user_id>/<int:flight_id>/<int:booking_id>/',views.ticket_generate,name='ticket_generate'),
    path('booking_summary/<int:user_id>/<int:flight_id>/<int:booking_id>/',views.booking_summary,name='booking_summary'),
    path('edit_passenger/<int:passenger_id>/',views.edit_passenger,name='edit_passenger'),
    path('payment_success/<int:booking_id>/',views.payment_success,name='payment_success'),
    path('cancel_ticket/<int:passenger_id>/', views.cancel_passenger_ticket, name='cancel_ticket'),
    path('generate_ticket_pdf/<int:user_id>/<int:flight_id>/<int:booking_id>/',views.generate_ticket_pdf,name='generate_pdf'),
    path('my_bookings/<int:user_id>/',views.my_bookings,name='my_bookings'),
    path('refund_policy/<int:user_id>/<int:booking_id>/<int:passenger_id>/',views.refund_policy,name='refund_policy'),

    #forget password urls

    path('forgot_password/',views.forget_password,name='forgot_password'),
    path('reset_password/<uidb64>/<token>/',views.reset_password,name='reset_password')

]

    
