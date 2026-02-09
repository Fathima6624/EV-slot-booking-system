from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking

def get_upcoming_reminder(user):
    now = timezone.now()
    reminder_window = now + timedelta(minutes=20)

    booking = Booking.objects.filter(
        user=user,
        status="booked",
        reminder_sent=False,
        slot__start_at__gte=now,
        slot__start_at__lte=reminder_window
    ).select_related(
        "slot__charging_point__station"
    ).first()

    return booking



from django.utils import timezone
from bookings.models import Booking

def update_completed_bookings():
    Booking.objects.filter(
        status="booked",
        slot__end_at__lt=timezone.now()
    ).update(status="completed")
