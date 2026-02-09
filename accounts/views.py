from django.shortcuts import render,redirect

from stations.models import ChargingStation,ChargingPoint

from slots.models import Slot
from django.contrib.auth.models import User
from .models import Profile

# Create your views here.

from accounts.models import Profile

from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking

def home(request):
    upcoming_booking = None

    if request.user.is_authenticated:
        profile, _ = Profile.objects.get_or_create(
            user=request.user,
            defaults={"role": "user"}
        )

        if profile.role == "operator":
            return redirect("operator_dashboard")

        now = timezone.now()
        upcoming_booking = Booking.objects.filter(
            user=request.user,
            status="booked",
            slot__start_at__gte=now,
            slot__start_at__lte=now + timedelta(minutes=20)
        ).select_related("slot__charging_point__station").first()

    return render(request, "home.html", {
        "upcoming_booking": upcoming_booking
    })









from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Logged in successfully")

            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")

    return render(request, "login.html")










from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, redirect

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # 1️⃣ Empty check
        if not all([full_name, email, password, confirm_password]):
            messages.error(request, "All fields are required")
            return render(request, "register.html")

        # 2️⃣ Password match
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "register.html")

        # 3️⃣ Existing user check
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return render(request, "register.html")

        # 4️⃣ Create user ONLY
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=full_name
        )

        # ❌ DO NOT CREATE PROFILE HERE
        # Profile is created automatically by signals.py

        messages.success(request, "Account created successfully. Please log in.")
        return redirect("login")

    return render(request, "register.html")









from django.contrib.auth import logout
from django.contrib import messages

def logout_view(request):
    logout(request)
    messages.get_messages(request)  # 🔥 clears old messages
    return redirect("login")




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from stations.models import ChargingStation
from .decorators import operator_only


from  django.utils import timezone

from stations.models import ChargingStation
from slots.models import Slot


@login_required
def operator_dashboard(request):
    if request.user.profile.role != "operator":
        return redirect("home")

    now = timezone.now()

    stations = ChargingStation.objects.filter(operator=request.user)

    total_stations = stations.count()

    total_points = (
        stations
        .prefetch_related("charging_points")
        .values_list("charging_points", flat=True)
        .count()
    )

    active_slots = Slot.objects.filter(
        charging_point__station__operator=request.user,
        is_active=True,
        end_at__gt=now
    ).count()

    return render(request, "operator_dashboard.html", {
        "total_stations": total_stations,
        "total_points": total_points,
        "active_slots": active_slots,
    })









