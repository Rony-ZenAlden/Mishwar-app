from rest_framework import serializers
from .models import TripStatus, User, Car, DriveInformationLicense, Trip, Complaint
from django.contrib.auth.hashers import make_password
from django.db.models import Avg


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password",
            "type",
            "driver_status",
            "lat",
            "lng",
        ]

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone"]  # Exclude password


class CarSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField()

    class Meta:
        model = Car
        fields = ["id", "driver", "car_color", "car_number", "car_model", "car_type"]


class DriveInformationLicenseSerializer(serializers.ModelSerializer):
    driver = serializers.StringRelatedField()

    class Meta:
        model = DriveInformationLicense
        fields = [
            "id",
            "driver",
            "first_name",
            "last_name",
            "birthday",
            "blood_type",
            "license_grant_date",
            "license_expiry_date",
            "license_number",
        ]


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = "__all__"


class UserSerializerForOneTrip(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class TripSerializerForUser(serializers.ModelSerializer):
    driver = UserSerializerForOneTrip(read_only=True)

    class Meta:
        model = Trip
        fields = [
            "driver",
            "destination_address",
            "status",
            "requested_at",
            "accepted_at",
            "started_at",
            "completed_at",
            "price",
            "rating",
        ]


class DriverSerializer(serializers.ModelSerializer):
    car_model = serializers.CharField(source="cars.first.car_model", read_only=True)
    car_type = serializers.CharField(source="cars.first.car_type", read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "average_rating",
            "lat",
            "lng",
            "car_model",
            "car_type",
        ]

    def get_average_rating(self, obj):
        completed_trips = obj.trips_driver.filter(
            status=TripStatus.COMPLETED, rating__isnull=False
        )
        if completed_trips.exists():
            avg = completed_trips.aggregate(Avg("rating"))["rating__avg"]
            return round(avg, 1)
        return None


class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            "id",
            "title",
            "description",
            "phone",
            "status",
            "created_at",
            "updated_at",
        ]
