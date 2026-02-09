from django.urls import path
from .views import station_list,operator_stations,add_station,manage_station,add_charging_point

urlpatterns = [
    path('', station_list, name='station_list'),
    path("operator/stations/", operator_stations, name="operator_stations"),
    path("operator/stations/add/", add_station, name="add_station"),
 path(
        "operator/stations/<int:station_id>/manage/",
        manage_station,
        name="manage_station"
    ),

    path(
    "operator/stations/<int:station_id>/add-point/",
    add_charging_point,
    name="add_charging_point"
),
  
]

