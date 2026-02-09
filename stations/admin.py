from django.contrib import admin

# Register your models here.

from .models import ChargingPoint,ChargingStation

admin.site.register(ChargingPoint)
admin.site.register(ChargingStation)