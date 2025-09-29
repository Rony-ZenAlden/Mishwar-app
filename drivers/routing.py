from django.urls import path
from . import consumers, consumers2

websocket_urlpatterns = [
    path("ws/driver_location/", consumers.DriverLocationConsumer.as_asgi()),
    path("ws/user/<int:user_id>/", consumers2.UserConsumer.as_asgi()),
    path("ws/driver/<int:driver_id>/", consumers2.DriverConsumer.as_asgi()),
    path("ws/trip/<int:trip_id>/", consumers2.TripConsumer.as_asgi()),
]
