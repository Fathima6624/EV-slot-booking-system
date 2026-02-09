from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from stations.models import ChargingStation
from django.db.models import Prefetch
from slots.models import Slot

@login_required
def station_list(request):
    stations = ChargingStation.objects.all()
    return render(request, "station_list.html", {"stations": stations})




from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .models import ChargingStation
from accounts.models import Profile

@login_required
def operator_stations(request):
    profile = request.user.profile

    if profile.role != "operator":
        return redirect("home")

    stations =  ChargingStation.objects.filter(operator=request.user)

    return render(
        request,
        "operator_stations.html",
        {"stations": stations}
    )

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages



@login_required
def add_station(request):
    # 🔒 Only operators can add stations
    if request.user.profile.role != "operator":
        return redirect("home")

    if request.method == "POST":
        name = request.POST.get("name")
        location = request.POST.get("location")
        address = request.POST.get("address")

        ChargingStation.objects.create(
            operator=request.user,
            name=name,
            location=location,
            address=address
        )

        messages.success(request, "Station added successfully")
        return redirect("operator_stations")

    return render(request, "add_station.html")


 


# operator side

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import ChargingStation
from slots.models import Slot
from .models import ChargingPoint


@login_required
def manage_station(request, station_id):
    # 🔒 Only operator
    if request.user.profile.role != "operator":
        return redirect("home")

    station = get_object_or_404(
        ChargingStation,
        id=station_id,
        operator=request.user
    )

    charging_points = station.charging_points.all()

    context = {
        "station": station,
        "charging_points": charging_points,
    }

    return render(request, "manage_station.html", context)

# operator

@login_required
def add_charging_point(request, station_id):
    station = get_object_or_404(
        ChargingStation,
        id=station_id,
        operator=request.user
    )

    if request.method == "POST":
        point_number = request.POST.get("point_number")
        connector_type = request.POST.get("connector_type")
        power_kw = request.POST.get("power_kw")

        ChargingPoint.objects.create(
            station=station,
            point_number=point_number,
            connector_type=connector_type,
            power_kw=power_kw
        )

        messages.success(request, "Charging point added")
        return redirect("manage_station", station_id=station.id)

    return render(request, "add_charging_point.html", {"station": station})
