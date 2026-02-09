# bookings/models.py
from django.db import models
from accounts.models import User
from slots.models import Slot

# bookings/models.py
class Booking(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'user'}
    )
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)

    booking_date = models.DateField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=(
            ('booked', 'Booked'),
            ('completed', 'Completed'),   # ✅ ADD THIS
            ('cancelled', 'Cancelled'),
        ),
        default='booked'
    )
    cancel_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.slot}"

 
