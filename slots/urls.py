from django.urls import path

from .views import station_slots,activate_slot,add_slot,operator_slot_list



urlpatterns = [
    path('<int:station_id>/', station_slots, name='station_slots'),
     path("activate/<int:slot_id>/", activate_slot, name="activate_slot"),
      path("add/<int:point_id>/", add_slot, name="add_slot"),
       path("charging-point/<int:point_id>/slots/",operator_slot_list,name="operator_slot_list" ),

]