from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone

from slots.models import Slot
from .models import Booking



@login_required
def confirm_booking(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)

    # 🔒 Safety checks
    if not slot.is_active:
        messages.error(request, "This slot is not active.")
        return redirect("station_slots", slot.charging_point.station.id)

    if slot.end_at <= timezone.now():
        messages.error(request, "This slot has expired.")
        return redirect("station_slots", slot.charging_point.station.id)

    if slot.is_booked:
        messages.error(request, "Slot already booked.")
        return redirect("station_slots", slot.charging_point.station.id)

    return render(request, "confirm_booking.html", {
        "slot": slot
    })




@login_required
def book_slot(request, slot_id):
    if request.method != "POST":
        return redirect("home")

    with transaction.atomic():
        slot = Slot.objects.select_for_update().get(id=slot_id)

        # 🔒 Final protection
        if not slot.is_active:
            messages.error(request, "Slot is not active.")
            return redirect("station_slots", slot.charging_point.station.id)

        if slot.end_at <= timezone.now():
            messages.error(request, "This slot has expired.")
            return redirect("station_slots", slot.charging_point.station.id)

        if slot.is_booked:
            messages.error(request, "Slot already booked.")
            return redirect("station_slots", slot.charging_point.station.id)

        Booking.objects.create(
            user=request.user,
            slot=slot,
            status="booked"
        )

    messages.success(request, "Booking confirmed successfully!")
    return redirect("station_slots", slot.charging_point.station.id)



@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )
    return render(request, "booking_success.html", {
        "booking": booking
    })

from .utils import update_completed_bookings

@login_required
def my_bookings(request):
    update_completed_bookings()  # ✅ ADD THIS

    now = timezone.now()

    upcoming = (
        Booking.objects
        .filter(user=request.user, status="booked", slot__end_at__gt=now)
        .select_related("slot__charging_point__station")
        .order_by("slot__start_at")
    )

    past = (
        Booking.objects
        .filter(user=request.user)
        .exclude(status="booked")
        .select_related("slot__charging_point__station")
        .order_by("-slot__start_at")
    )

    return render(request, "my_bookings.html", {
        "upcoming": upcoming,
        "past": past
    })





from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Booking


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user,
        status="booked"
    )

    # ❌ Prevent cancelling completed bookings
    if booking.slot.end_at <= timezone.now():
        messages.error(request, "Cannot cancel a completed booking.")
        return redirect("my_bookings")

    if request.method == "POST":
        cancel_reason = request.POST.get("cancel_reason")

        booking.status = "cancelled"
        booking.cancel_reason = cancel_reason  # ✅ save reason
        booking.save()

        messages.success(request, "Your booking has been cancelled.")
        return redirect("my_bookings")

    return redirect("my_bookings")






@login_required
def booking_receipt(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    return render(request, "booking_receipt.html", {
        "booking": booking
    })




from django.utils import timezone

@login_required
def operator_bookings(request):
    bookings = (
        Booking.objects
        .filter(slot__charging_point__station__operator=request.user)
        .select_related("user", "slot__charging_point__station")
        .order_by("-slot__start_at")
    )

    return render(request, "operator_bookings.html", {
        "bookings": bookings,
        "now": timezone.now(),   # 👈 needed for Completed status
    })

