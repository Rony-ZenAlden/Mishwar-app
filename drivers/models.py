from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = "admin", _("Admin")
        DRIVER = "driver", _("Driver")
        CLIENT = "client", _("Client")

    class DriverStatus(models.TextChoices):
        ONLINE = "online", _("Online")
        OFFLINE = "offline", _("Offline")
        BUSY = "busy", _("Busy")

    phone = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Phone")
    )
    type = models.CharField(
        max_length=10, choices=UserType.choices, default=UserType.DRIVER
    )
    # New field for driver status
    driver_status = models.CharField(
        max_length=10,
        choices=DriverStatus.choices,
        default=DriverStatus.OFFLINE,
        verbose_name=_("Driver Status"),
    )
    lat = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Latitude"),
    )
    lng = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name=_("Longitude"),
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Average Rating"),
    )

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = _("All User")


class Car(models.Model):
    driver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="cars",
        limit_choices_to={"type": User.UserType.DRIVER},
    )
    car_color = models.CharField(max_length=50)
    car_number = models.CharField(max_length=50, unique=True)
    car_model = models.CharField(max_length=50)
    car_type = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.car_model} - {self.car_number}"


class DriveInformationLicense(models.Model):

    driver = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="information",
        limit_choices_to={"type": User.UserType.DRIVER},
    )

    first_name = models.CharField(max_length=50, verbose_name="First Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    birthday = models.DateField(verbose_name="Date of Birth")
    blood_type = models.CharField(
        max_length=3,
        verbose_name="Blood Type",
    )
    license_grant_date = models.DateField(verbose_name="License Grant Date")
    license_expiry_date = models.DateField(verbose_name="License Expiry Date")
    license_number = models.IntegerField(verbose_name="License Number")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.blood_type}"


class TripStatus(models.TextChoices):
    REQUESTED = "requested", _("Requested")
    ACCEPTED = "accepted", _("Accepted")
    STARTED = "started", _("Started")
    COMPLETED = "completed", _("Completed")
    CANCELLED = "cancelled", _("Cancelled")


PAYMENT_METHOD_CHOICES = [
    ("ONLINE", "Online"),
    ("CASH", "Cash"),
]

PAYMENT_STATUS_CHOICES = [
    ("PENDING", "Pending"),
    ("PAID", "Paid"),
    ("FAILED", "Failed"),
]


class Trip(models.Model):
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="trips_client"
    )
    driver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trips_driver",
    )
    payment_method = models.CharField(
        max_length=10, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True
    )
    payment_status = models.CharField(
        max_length=10, choices=PAYMENT_STATUS_CHOICES, default="PENDING"
    )
    start_lat = models.DecimalField(max_digits=9, decimal_places=6)
    start_lng = models.DecimalField(max_digits=9, decimal_places=6)
    destination_address = models.CharField(max_length=255)
    destination_lat = models.DecimalField(max_digits=9, decimal_places=6)
    destination_lng = models.DecimalField(max_digits=9, decimal_places=6)
    status = models.CharField(
        max_length=20, choices=TripStatus.choices, default=TripStatus.REQUESTED
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True)
    review = models.TextField(null=True, blank=True)
    history = models.JSONField(
        default=list, blank=True
    )  ##################################??????????????????????

    def __str__(self):
        return f"Trip #{self.id} from ({self.start_lat}, {self.start_lng}) to {self.destination_address}"


class Complaint(models.Model):
    class ComplaintStatus(models.TextChoices):
        PENDING = "pending", _("Pending")
        RESOLVED = "resolved", _("Resolved")
        IN_PROGRESS = "in_progress", _("In Progress")

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="complaints")
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    phone = models.CharField(
        max_length=15, blank=True, null=True, verbose_name=_("Phone")
    )
    description = models.TextField(verbose_name=_("Description"))
    status = models.CharField(
        max_length=20,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.PENDING,
        verbose_name=_("Status"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    def __str__(self):
        return f"Complaint #{self.id} by {self.user.username}"

    class Meta:
        verbose_name = _("Complaint")
        verbose_name_plural = _("Complaints")
        ordering = ["-created_at"]


# class Rating(models.Model):
#     driver = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="ratings",
#         limit_choices_to={"type": User.UserType.DRIVER},
#     )
#     client = models.ForeignKey(
#         User,
#         on_delete=models.CASCADE,
#         related_name="given_ratings",
#         limit_choices_to={"type": User.UserType.CLIENT},
#     )
#     rating = models.DecimalField(
#         max_digits=2, decimal_places=1, verbose_name=_("Rating")
#     )
#     created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

#     class Meta:
#         verbose_name = _("Rating")
#         verbose_name_plural = _("Ratings")
#         unique_together = (
#             "driver",
#             "client",
#         )

#     def __str__(self):
#         return f"{self.client.username} -> {self.driver.username}: {self.rating}"
