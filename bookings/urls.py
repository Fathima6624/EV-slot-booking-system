from django.urls import path

from .views import book_slot,my_bookings,booking_success,cancel_booking,confirm_booking,booking_receipt,operator_bookings

urlpatterns = [
     path('book/<int:slot_id>/', book_slot, name='book_slot'),
     path('success/<int:booking_id>/', booking_success, name='booking_success'),
    path('mybookings/', my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
     path("confirm/<int:slot_id>/", confirm_booking, name="confirm_booking"),
     path("receipt/<int:booking_id>/", booking_receipt, name="booking_receipt"),
      path("operator/", operator_bookings, name="operator_bookings"),


               ]