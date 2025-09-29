import asyncio
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from ..models import Trip, User, TripStatus
from ..serializer import TripSerializer, TripSerializerForUser
from django.utils import timezone
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
import time
from math import radians, sin, cos, sqrt, atan2
from django.db.models import Q


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def trip_request_view(request):
    serializer = TripSerializer(data=request.data)
    if serializer.is_valid():
        trip = serializer.save(client=request.user, status=TripStatus.REQUESTED)
        async_to_sync(expand_radius_and_notify_drivers)(trip)
        return Response(
            {
                "message": "Trip requested successfully",
                "trip_id": trip.id,
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def my_trips_list(request):
    # Get trips ordered by newest first
    trips = (
        Trip.objects.filter(Q(client=request.user) | Q(driver=request.user))
        .distinct()
        .order_by("-requested_at")
    )  # Assuming your timestamp field is called requested_at

    serializer = TripSerializerForUser(trips, many=True)
    return Response(serializer.data)


def haversine(coord1, coord2):
    R = 6371.0
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = (
        sin(dlat / 2) ** 2
        + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    )
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_trip(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id)
        if (
            trip.status != TripStatus.REQUESTED
            or request.user.type != User.UserType.DRIVER
        ):
            return Response(
                {"error": "Trip is not available for acceptance"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip.driver = request.user
        trip.status = TripStatus.ACCEPTED
        trip.accepted_at = timezone.now()
        trip.save()

        driver_lat = float(request.user.lat)
        driver_lng = float(request.user.lng)
        start_lat = float(trip.start_lat)
        start_lng = float(trip.start_lng)
        distance = haversine((start_lat, start_lng), (driver_lat, driver_lng))
        duration = f"{int(distance / 0.1)} mins"

        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            f"user_{trip.client.id}",
            {
                "type": "trip_status",
                "status": "accepted",
                "message": "Your trip has been accepted.",
                "trip_id": trip.id,
                "driver_phone": request.user.phone,
                "driver_lat": driver_lat,
                "driver_lng": driver_lng,
                "distance": f"{distance:.2f} km",
                "duration": duration,
            },
        )

        async_to_sync(channel_layer.group_send)(
            f"driver_{request.user.id}",
            {
                "type": "trip_accepted",
                "trip_id": trip.id,
                "user_phone": trip.client.phone,
                "user_lat": str(trip.start_lat),
                "user_lng": str(trip.start_lng),
                "destination_address": trip.destination_address,
                "destination_lat": str(trip.destination_lat),
                "destination_lng": str(trip.destination_lng),
            },
        )

        return Response(
            {
                "message": "Trip accepted",
                "user_phone": trip.client.phone,
                "driver_phone": request.user.phone,
                "trip_id": trip.id,
                "user_lat": str(trip.start_lat),
                "user_lng": str(trip.start_lng),
                "destination_address": trip.destination_address,
                "destination_lat": str(trip.destination_lat),
                "destination_lng": str(trip.destination_lng),
                "driver_lat": driver_lat,
                "driver_lng": driver_lng,
                "distance": f"{distance:.2f} km",
                "duration": duration,
            },
            status=status.HTTP_200_OK,
        )
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)
    except ValueError as e:
        return Response(
            {"error": f"Invalid coordinate data: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def driver_arrived(request, trip_id):
    try:
        trip = Trip.objects.get(
            id=trip_id, driver=request.user, status=TripStatus.ACCEPTED
        )
        trip.status = TripStatus.STARTED
        trip.started_at = timezone.now()
        trip.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"trip_{trip.id}",
            {
                "type": "trip_started",
                "trip_id": trip.id,
                "start_lat": str(trip.start_lat),
                "start_lng": str(trip.start_lng),
                "destination_lat": str(trip.destination_lat),
                "destination_lng": str(trip.destination_lng),
            },
        )
        return Response({"message": "Trip started"}, status=status.HTTP_200_OK)
    except Trip.DoesNotExist:
        return Response(
            {"error": "Trip not found or not authorized"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def complete_trip(request, trip_id):
    try:
        trip = Trip.objects.get(
            id=trip_id, driver=request.user, status=TripStatus.STARTED
        )
        trip.status = TripStatus.COMPLETED
        trip.completed_at = timezone.now()

        # Calculate distance
        start_coord = (float(trip.start_lat), float(trip.start_lng))
        dest_coord = (float(trip.destination_lat), float(trip.destination_lng))
        distance = haversine(start_coord, dest_coord)

        # Define rate per kilometer
        rate_per_km = 2.0  # $2 per km

        # Calculate price
        price = distance * rate_per_km
        trip.price = round(price, 2)
        trip.payment_status = "PENDING"  # Set payment status to PENDING
        trip.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"trip_{trip.id}",
            {
                "type": "trip_ended",
                "trip_id": trip.id,
                "start_lat": str(trip.start_lat),
                "start_lng": str(trip.start_lng),
                "destination_lat": str(trip.destination_lat),
                "destination_lng": str(trip.destination_lng),
                "price": str(trip.price),  # Send price as string for JSON compatibility
            },
        )
        return Response({"message": "Trip completed"}, status=status.HTTP_200_OK)
    except Trip.DoesNotExist:
        return Response(
            {"error": "Trip not found or not authorized"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def rate_trip(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, client=request.user)
        if trip.status != TripStatus.COMPLETED:
            return Response(
                {"error": "Trip is not completed"}, status=status.HTTP_400_BAD_REQUEST
            )
        if trip.payment_status != "PAID":
            return Response(
                {"error": "Payment is not completed"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if trip.rating is not None:
            return Response(
                {"error": "Trip already rated"}, status=status.HTTP_400_BAD_REQUEST
            )

        rating = request.data.get("rating")
        review = request.data.get("review", "")

        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return Response(
                {"error": "Invalid rating. Must be an integer between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        trip.rating = rating
        trip.review = review
        trip.save()

        return Response(
            {"message": "Rating submitted successfully"}, status=status.HTTP_200_OK
        )
    except Trip.DoesNotExist:
        return Response(
            {"error": "Trip not found or not authorized"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def select_payment_method(request, trip_id):
    try:
        trip = Trip.objects.get(
            id=trip_id,
            client=request.user,
            status=TripStatus.COMPLETED,
            payment_status="PENDING",
        )
        payment_method = request.data.get("payment_method")
        if payment_method not in ["ONLINE", "CASH"]:
            return Response(
                {"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST
            )
        trip.payment_method = payment_method
        trip.save()

        if payment_method == "CASH":
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"driver_{trip.driver.id}",
                {
                    "type": "cash_payment_selected",
                    "trip_id": trip.id,
                    "price": str(trip.price),
                },
            )

        return Response(
            {"message": "Payment method selected"}, status=status.HTTP_200_OK
        )
    except Trip.DoesNotExist:
        return Response(
            {"error": "Trip not found or not authorized"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_online_payment(request, trip_id):
    try:
        trip = Trip.objects.get(
            id=trip_id,
            client=request.user,
            status=TripStatus.COMPLETED,
            payment_method="ONLINE",
            payment_status="PENDING",
        )
        trip.payment_status = "PAID"
        trip.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"driver_{trip.driver.id}",
            {
                "type": "payment_confirmed",
                "trip_id": trip.id,
                "message": "The user has completed the online payment.",
            },
        )

        return Response(
            {"message": "Online payment confirmed"}, status=status.HTTP_200_OK
        )
    except Trip.DoesNotExist:
        return Response(
            {"error": "Trip not found or not authorized"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def confirm_cash_payment(request, trip_id):
    try:
        trip = Trip.objects.get(
            id=trip_id,
            driver=request.user,
            status=TripStatus.COMPLETED,
            payment_method="CASH",
            payment_status="PENDING",
        )
        trip.payment_status = "PAID"
        trip.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{trip.client.id}",
            {
                "type": "payment_confirmed",
                "trip_id": trip.id,
                "message": "Your cash payment has been confirmed by the driver.",
            },
        )

        return Response(
            {"message": "Cash payment confirmed"}, status=status.HTTP_200_OK
        )
    except Trip.DoesNotExist:
        return Response(
            {"error": "Trip not found or not authorized"},
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_trip_details(request, trip_id):
    try:
        trip = Trip.objects.get(id=trip_id, client=request.user)
        if trip.status == TripStatus.ACCEPTED and trip.driver:
            driver_lat = float(trip.driver.lat)
            driver_lng = float(trip.driver.lng)
            start_lat = float(trip.start_lat)
            start_lng = float(trip.start_lng)
            distance = haversine((start_lat, start_lng), (driver_lat, driver_lng))
            duration = f"{int(distance / 0.1)} mins"

            return Response(
                {
                    "status": trip.status,
                    "driver_phone": trip.driver.phone,
                    "trip_id": trip.id,
                    "driver_lat": driver_lat,
                    "driver_lng": driver_lng,
                    "distance": f"{distance:.2f} km",
                    "duration": duration,
                },
                status=status.HTTP_200_OK,
            )
        return Response({"status": trip.status}, status=status.HTTP_200_OK)
    except Trip.DoesNotExist:
        return Response({"error": "Trip not found"}, status=status.HTTP_404_NOT_FOUND)


async def expand_radius_and_notify_drivers(trip):
    notified_drivers = set()
    current_radius = 20
    max_radius = 100

    while current_radius <= max_radius:
        drivers = await get_drivers_in_radius(
            trip.start_lat, trip.start_lng, current_radius
        )
        drivers_to_notify = [
            driver for driver in drivers if driver.id not in notified_drivers
        ]
        if drivers_to_notify:
            print(
                f"Found {len(drivers_to_notify)} new drivers within {current_radius} km"
            )
            await notify_drivers(trip, drivers_to_notify)
            notified_drivers.update([driver.id for driver in drivers_to_notify])
            await asyncio.sleep(5)
            trip = await sync_to_async(Trip.objects.select_related("client").get)(
                id=trip.id
            )
            if trip.status == TripStatus.ACCEPTED:
                print(f"Trip {trip.id} accepted, exiting radius expansion")
                return
        current_radius *= 2

    print(f"No drivers accepted trip {trip.id}, notifying user")
    await notify_user_trip_not_accepted(trip.client)


async def get_drivers_in_radius(start_lat, start_lng, radius_km):
    drivers = await sync_to_async(list)(
        User.objects.filter(
            type=User.UserType.DRIVER, driver_status=User.DriverStatus.ONLINE
        )
    )
    start_point = (float(start_lat), float(start_lng))
    nearby_drivers = []
    for driver in drivers:
        if driver.lat and driver.lng:
            driver_point = (float(driver.lat), float(driver.lng))
            distance = haversine(start_point, driver_point)
            if distance <= radius_km:
                nearby_drivers.append(driver)
    return nearby_drivers


async def notify_drivers(trip, drivers):
    channel_layer = get_channel_layer()
    for driver in drivers:
        print(f"Notifying driver {driver.id} about trip {trip.id}")
        await channel_layer.group_send(
            f"driver_{driver.id}",
            {
                "type": "trip_request",
                "trip_id": trip.id,
                "start_lat": str(trip.start_lat),
                "start_lng": str(trip.start_lng),
                "destination": trip.destination_address,
                "destination_lat": str(trip.destination_lat),
                "destination_lng": str(trip.destination_lng),
            },
        )


async def notify_user_trip_not_accepted(user):
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        f"user_{user.id}",
        {
            "type": "trip_status",
            "status": "not_accepted",
            "message": "Your trip request was not accepted.",
        },
    )
