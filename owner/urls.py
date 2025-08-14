from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('ownerindex/',views.ownerindex,name='ownerindex'),
    path('flightregister/',views.flightregister,name='flightregister'),
    path('flightlogin/',views.flightlogin,name='flightlogin'),
    path('flightdashboard/<int:user_id>/',views.flightdashboard,name='flightdashboard'),
    path('hotelregister/',views.hotelregister,name='hotelregister'),
    path('hotellogin/',views.hotellogin,name='hotellogin'),
    path('hoteldashboard/<int:hotel_id>/',views.hoteldashboard,name='hoteldashboard'),
    path('hotel_logout/',views.hotel_logout,name='hotel_logout'),
    

    #flight dashboard

    path('aircraft_registration/<int:user_id>/',views.aircraft_registration,name='aircraft'),
    
    path('owner/view_aircraft/<int:user_id>/', views.view_aircraft, name='viewaircraft'),
    path('add_flight/<int:user_id>/',views.add_flight,name='add_flight'),
    path('owner/view_flight/<int:user_id>/',views.view_flight,name='viewflight'),
    path('owner/update_flight/<int:user_id>/<int:flight_id>/',views.update_flight,name='updateflight'),
    path('flightlogout/',views.flightlogout,name='flightlogout'),
    path('delete_flight/<int:user_id>/<int:flight_id>/',views.delete_flight,name='delete_flight'),
    path('owner/owner_view_bookings/<int:user_id>/',views.owner_view_bookings,name='owner_view_bookings'),
    
    #hotel search
    path("search_hotels/", views.hotel_search_view, name="hotel_search"),
    # hotel owner dashboard
    path('add_new_booking/<int:hotel_id>/',views.add_new_booking,name='add_new_booking'),
    path('add_rooms/<int:hotel_id>/',views.add_room,name='add_rooms'),
    path('add_room_type/<int:hotel_id>/',views.add_room_type,name='add_room_type'),
    path('owner/manage_rooms/<int:hotel_id>/',views.manage_rooms,name='manage_rooms'),
    path('owner/delete_room/<int:hotel_id>/<int:room_id>/', views.delete_rooms, name='delete_room'),
    path('owner/view_room/<int:hotel_id>/<int:room_id>/',views.view_rooms,name='view_room'),

    # hotel search page for user

    path('hotel_search/<int:user_id>/',views.hotel_search,name='hotel_search'),
    path('avaliable_hotel/<int:user_id>/',views.avaliable_hotel,name='avaliable_hotel'),
    path('select_rooms/<int:user_id>/<int:hotel_id>/',views.select_rooms,name='select_rooms'),
    path('book-room/<int:user_id>/<int:booking_id>/', views.book_room, name='book_room'),
    
    path('guest_info/<int:user_id>/<int:room_id>/',views.guest_info,name='guest_info'),
    path('payment_success/',views.payment_success,name='payment_success'),
    path('payment-success-view/<int:booking_id>/<int:user_id>', views.payment_success_view, name='payment_success_view'),
    path('hotel_my_bookings/<int:user_id>/',views.hotel_my_bookings,name='hotel_my_bookings'),
    path('cancel-hotel-bookings/<int:booking_id>/',views.cancel_hotel_bookings,name='cancel_hotel_bookings'),
    path('manage_guests/<int:hotel_id>/',views.manage_guests,name='manage_guests'),
    path('manage_bookings/<int:hotel_id>/',views.manage_bookings,name='manage_bookings'),
    path('delete_bookings/<int:hotel_id>/<int:booking_id>/',views.delete_booking,name='delete_bookings'),
    

    



    


    
]

