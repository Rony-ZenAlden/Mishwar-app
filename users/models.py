from django.db import models

# class ActiveNearbyAvailableDrivers(models.Model):
#     driver = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="active_locations",
#         limit_choices_to={"type": User.UserType.DRIVER},
#     )
#     location_latitude = models.FloatField()
#     location_longitude = models.FloatField()

#     def __str__(self):
#         return f"{self.driver.username} - ({self.location_latitude}, {self.location_longitude})"


# class DirectionDetailsInfo(models.Model):
#     distance_value = models.IntegerField(blank=True, null=True)
#     duration_value = models.IntegerField(blank=True, null=True)
#     e_points = models.TextField(blank=True, null=True)
#     distance_text = models.CharField(max_length=255, blank=True, null=True)
#     duration_text = models.CharField(max_length=255, blank=True, null=True)

#     def __str__(self):
#         return f"{self.distance_text} - {self.duration_text}"


# class PredictedPlaces(models.Model):
#     place_id = models.CharField(max_length=255, blank=True, null=True)
#     main_text = models.CharField(max_length=255, blank=True, null=True)
#     secondary_text = models.CharField(max_length=255, blank=True, null=True)

#     def __str__(self):
#         return self.main_text or "Unnamed Place"


# class TripsHistoryModel(models.Model):
#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="trip_history"
#     )
#     driver = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="completed_trips",
#         limit_choices_to={"type": User.UserType.DRIVER},
#     )
#     car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="trips")
#     time = models.DateTimeField(blank=True, null=True)
#     origin_address = models.CharField(max_length=255, blank=True, null=True)
#     destination_address = models.CharField(max_length=255, blank=True, null=True)
#     status = models.CharField(max_length=50, blank=True, null=True)
#     fare_amount = models.DecimalField(
#         max_digits=10, decimal_places=2, blank=True, null=True
#     )

#     def __str__(self):
#         return f"{self.origin_address} to {self.destination_address} - {self.status}"


# class UserRideRequestInformation(models.Model):
#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="ride_requests"
#     )
#     driver = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="accepted_requests",
#         limit_choices_to={"type": User.UserType.DRIVER},
#     )
#     origin_latitude = models.FloatField()
#     origin_longitude = models.FloatField()
#     destination_latitude = models.FloatField()
#     destination_longitude = models.FloatField()
#     origin_address = models.CharField(max_length=255)
#     destination_address = models.CharField(max_length=255)
#     ride_request_id = models.CharField(max_length=100, unique=True)
#     user_name = models.CharField(max_length=100)
#     user_phone = models.CharField(max_length=15)

#     def __str__(self):
#         return f"Ride Request {self.ride_request_id} by {self.user_name}"


# class Directions(models.Model):
#     human_readable_address = models.CharField(max_length=255, blank=True, null=True)
#     location_name = models.CharField(max_length=255, blank=True, null=True)
#     location_id = models.CharField(max_length=255, blank=True, null=True)
#     location_latitude = models.FloatField(blank=True, null=True)
#     location_longitude = models.FloatField(blank=True, null=True)

#     def __str__(self):
#         return self.location_name or "Unnamed Location"
