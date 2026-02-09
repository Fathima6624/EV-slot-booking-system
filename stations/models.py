from django.db import models
from django.contrib.auth.models import User

class ChargingStation(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, default="")

    operator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'profile__role': 'operator'},
        null=True,
        blank=True
    )

    contact_number = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ChargingPoint(models.Model):
    station = models.ForeignKey(
        ChargingStation,
        on_delete=models.CASCADE,
        related_name='charging_points'
    )

    point_number = models.CharField(max_length=50)

    connector_type = models.CharField(
        max_length=20,
        choices=[
            ('type2', 'Type 2'),
            ('ccs', 'CCS'),
            ('chademo', 'CHAdeMO')
        ],
        default='type2'
    )

    power_kw = models.PositiveIntegerField(default=7)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.station.name} - Point {self.point_number}"
