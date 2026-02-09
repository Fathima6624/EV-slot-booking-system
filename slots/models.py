from django.db import models
from stations.models import ChargingPoint

from django.utils import timezone


class Slot(models.Model):
    charging_point = models.ForeignKey(
        ChargingPoint,
        on_delete=models.CASCADE,
        related_name="slots"
    )

    start_at = models.DateTimeField()
    end_at = models.DateTimeField()

    is_active = models.BooleanField(default=True)

    @property
    def is_booked(self):
        return self.booking_set.filter(status="booked").exists()

    @property
    def is_available(self):
        now = timezone.now()
        return (
            self.is_active and
            self.start_at > now and
            not self.is_booked
        )


