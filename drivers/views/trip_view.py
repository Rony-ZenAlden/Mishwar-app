# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from ..models import User
from decimal import Decimal

###################### Driver Location ######################
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User
from ..serializer import DriverSerializer
from math import radians, cos, sin, asin, sqrt
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ObjectDoesNotExist


def haversine(lat1, lon1, lat2, lon2):
    lon1, lat1, lon2, lat2 = map(
        radians, [float(lon1), float(lat1), float(lon2), float(lat2)]
    )
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r


# @api_view(["GET"])
# def getNearbyDrivers(request):
#     user_lat = request.query_params.get("lat")
#     user_lng = request.query_params.get("lng")

#     if not user_lat or not user_lng:
#         return Response(
#             {"error": "Latitude and longitude are required"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     try:
#         user_lat = Decimal(user_lat)
#         user_lng = Decimal(user_lng)
#     except InvalidOperation:
#         return Response(
#             {"error": "Invalid latitude or longitude"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     online_drivers = User.objects.filter(type="driver", driver_status="online")
#     nearby_drivers = []

#     for driver in online_drivers:
#         if driver.lat and driver.lng:
#             distance = haversine(user_lat, user_lng, driver.lat, driver.lng)
#             if distance <= 40:  # 10 km radius
#                 nearby_drivers.append(driver)

#     serializer = DriverSerializer(nearby_drivers, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def getNearbyDrivers(request):
    # Retrieve all online drivers that have location data
    online_drivers = User.objects.filter(
        type="driver",
        driver_status="online",
        lat__isnull=False,
        lng__isnull=False,
    )

    serializer = DriverSerializer(online_drivers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def updateDriverLocation(request):
    driver_id = request.data.get("driver_id")
    lat = request.data.get("lat")
    lng = request.data.get("lng")

    if not driver_id or not lat or not lng:
        return Response(
            {"error": "Driver ID, latitude, and longitude are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        driver = User.objects.get(id=driver_id, type="driver")
        driver.lat = lat
        driver.lng = lng
        driver.is_online = True
        driver.save()
        return Response(
            {"message": "Location updated successfully"}, status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def updateUserLocation(request):
    user_id = request.data.get("user_id")
    lat = request.data.get("lat")
    lng = request.data.get("lng")

    if not all([user_id, lat, lng]):
        return Response(
            {"error": "Missing parameters"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        user.lat = Decimal(str(lat))
        user.lng = Decimal(str(lng))
        user.save()
        return Response({"status": "Location updated"}, status=status.HTTP_200_OK)
    except InvalidOperation:
        return Response(
            {"error": "Invalid latitude or longitude format"},
            status=status.HTTP_400_BAD_REQUEST,
        )
