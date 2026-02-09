from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.contrib import messages
from django.utils import timezone

from accounts.models import Profile
from stations.models import ChargingStation, ChargingPoint
from slots.models import Slot


@login_required
def station_slots(request, station_id):
    station = get_object_or_404(ChargingStation, id=station_id)

    charging_points = station.charging_points.prefetch_related(
        Prefetch(
            "slots",
            queryset=Slot.objects.filter(
                is_active=True,
                end_at__gt=timezone.now()   # 🔥 hide expired slots
            ).order_by("start_at")
        )
    )

    return render(request, "slot_list.html", {
        "station": station,
        "charging_points": charging_points,
    })



from datetime import datetime
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.models import Profile
from stations.models import ChargingPoint
from slots.models import Slot


@login_required
def add_slot(request, point_id):
    point = get_object_or_404(ChargingPoint, id=point_id)

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "user"}
    )

    # 🔒 Operator only
    if profile.role != "operator":
        return redirect("home")

    # 🔒 Ownership check
    if point.station.operator != request.user:
        return redirect("operator_dashboard")

    if request.method == "POST":
        date = request.POST.get("date")
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")

        # 🚫 Safety check
        if not all([date, start_time, end_time]):
            messages.error(request, "All fields are required")
            return redirect("add_slot", point_id=point.id)

        # 🧠 Combine date + time → datetime
        start_naive = datetime.strptime(
            f"{date} {start_time}", "%Y-%m-%d %H:%M"
        )
        end_naive = datetime.strptime(
            f"{date} {end_time}", "%Y-%m-%d %H:%M"
        )

        # 🌍 Make timezone aware
        start_at = timezone.make_aware(start_naive)
        end_at = timezone.make_aware(end_naive)

        # ⛔ Invalid time range
        if start_at >= end_at:
            messages.error(request, "End time must be after start time")
            return redirect("add_slot", point_id=point.id)

        # ⛔ Prevent overlapping slots (same day, same point)
        overlap = Slot.objects.filter(
            charging_point=point,
            start_at__lt=end_at,
            end_at__gt=start_at
        ).exists()

        if overlap:
            messages.error(request, "Slot overlaps with an existing slot")
            return redirect("add_slot", point_id=point.id)

        # ✅ Create slot (inactive by default)
        Slot.objects.create(
            charging_point=point,
            start_at=start_at,
            end_at=end_at,
            is_active=False
        )

        messages.success(request, "Slot created successfully. Activate when ready.")
        return redirect("operator_dashboard")

    return render(request, "add_slot.html", {"point": point})





@login_required
def activate_slot(request, slot_id):
    if request.method != "POST":
        return redirect("operator_dashboard")

    slot = get_object_or_404(Slot, id=slot_id)

    profile, _ = Profile.objects.get_or_create(
        user=request.user,
        defaults={"role": "user"}
    )

    # 🔒 Operator only
    if profile.role != "operator":
        return redirect("home")

    # 🔒 Ownership check
    if slot.charging_point.station.operator != request.user:
        return redirect("operator_dashboard")

    # ⛔ Prevent activating expired slot
    if slot.end_at <= timezone.now():
        messages.error(request, "Cannot activate an expired slot")
        return redirect("operator_dashboard")

    slot.is_active = True
    slot.save()

    messages.success(request, "Slot activated successfully")
    return redirect("operator_dashboard")


# for operator

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from stations.models import ChargingPoint
from .models import Slot

from django.utils import timezone




from django.utils import timezone

@login_required
def operator_slot_list(request, point_id):
    charging_point = get_object_or_404(
        ChargingPoint,
        id=point_id,
        station__operator=request.user
    )

    now = timezone.now()

    # 🔁 Auto-disable expired slots
    Slot.objects.filter(
        charging_point=charging_point,
        end_at__lte=now,
        is_active=True
    ).update(is_active=False)

    slots = Slot.objects.filter(
        charging_point=charging_point
    ).order_by("start_at")

    return render(
        request,
        "operator_slot_list.html",
        {
            "charging_point": charging_point,
            "slots": slots,
            "now": now,
        }
    )






