import random
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello World")


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from ..models import User, Car, DriveInformationLicense
from ..serializer import (
    UserSerializer,
    CarSerializer,
    DriveInformationLicenseSerializer,
    UserUpdateSerializer,
)
from drf_yasg.utils import swagger_auto_schema


####################### User APIs ######################
@swagger_auto_schema(
    method="POST",
    request_body=UserSerializer,
    responses={"200": UserSerializer, "400": "bad req"},
    operation_description="thoksjal ahjfjkh",
)
@api_view(["GET", "POST"])
def user_list_create(request):

    if request.method == "GET":
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"user": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def user_detail(request, pk):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


####################### Car APIs ######################
@api_view(["GET"])
def car_list_getAll(request):
    cars = Car.objects.all()
    serializer = CarSerializer(cars, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def car_list_create(request, username):
    try:
        driver = User.objects.get(username=username, type=User.UserType.DRIVER)
    except User.DoesNotExist:
        return Response(
            {"error": "Driver not found or user is not a driver"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = CarSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save(driver=driver)
        return Response({"carId": instance.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def car_detail(request, pk):
    try:
        car = Car.objects.get(pk=pk)
    except Car.DoesNotExist:
        return Response({"error": "Car not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = CarSerializer(car)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = CarSerializer(car, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        car.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


############## DriveInformationLicense APIs ######################
@api_view(["GET"])
def drive_information_list_get(request):
    info = DriveInformationLicense.objects.all()
    serializer = DriveInformationLicenseSerializer(info, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def drive_information_list_create(request, username):
    try:
        driver = User.objects.get(username=username, type=User.UserType.DRIVER)
    except User.DoesNotExist:
        return Response(
            {"error": "Driver not found or user is not a driver"},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = DriveInformationLicenseSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save(driver=driver)
        return Response({"licenseId": instance.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "DELETE"])
def drive_information_detail(request, pk):
    try:
        info = DriveInformationLicense.objects.get(pk=pk)
    except DriveInformationLicense.DoesNotExist:
        return Response(
            {"error": "Information not found"}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "GET":
        serializer = DriveInformationLicenseSerializer(info)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = DriveInformationLicenseSerializer(info, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        info.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


################## Authentication ################################
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


@api_view(["GET"])
def driver_details(request, driver_id):
    try:
        driver = User.objects.get(pk=driver_id)
    except driver.DoesNotExist:
        return Response({"error": "Driver not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get LicenseID from DriveInformationLicense
    license_info = driver.information  # Use correct related_name
    license_id = license_info.id if license_info else None

    # Get CarId from Car (assuming one car, taking the first if multiple exist)
    car = driver.cars.first()
    car_id = car.id if car else None

    response_data = {
        "LicenseID": license_id,
        "CarId": car_id,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(["POST"])
def user_login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Authenticate user
    user = authenticate(request, username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials or inactive account"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if not user.is_active:
        return Response(
            {"error": "Your account is not active. Please contact support."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = TokenObtainPairSerializer(
        data={"username": username, "password": password}
    )

    if serializer.is_valid():
        tokens = serializer.validated_data  # Get generated tokens

        return Response(
            {
                "userID": user.id,
                "username": user.username,
                "phone": user.phone,
                "access": tokens["access"],
                "refresh": tokens["refresh"],
            },
            status=status.HTTP_200_OK,
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


################## Change Password Verfication Api ################################
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

User = get_user_model()


def generate_otp():
    return str(random.randint(100000, 999999))


def send_reset_email(user, otp):
    subject = "Password Reset Request"
    message = f"Hello {user.username},\n\nYour OTP for password reset is: {otp}\nIt will expire in 3 minutes.\n\nThank you."  # Updated expiration time
    from_email = "noreply@yourdomain.com"
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)


@api_view(["POST"])
def password_reset_request(request):
    """API to handle password reset request by sending a 6-digit OTP to the user's email."""

    class PasswordResetRequestSerializer(serializers.Serializer):
        email = serializers.EmailField()

    serializer = PasswordResetRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    otp = generate_otp()
    cache.set(f"password_reset_{email}", otp, timeout=180)
    send_reset_email(user, otp)

    return Response({"message": "OTP sent to email"})


@api_view(["POST"])
def password_reset_verify(request):
    class PasswordResetVerifySerializer(serializers.Serializer):
        email = serializers.EmailField()
        otp = serializers.CharField()
        new_password = serializers.CharField(write_only=True)

    serializer = PasswordResetVerifySerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    otp = serializer.validated_data["otp"]
    new_password = serializer.validated_data["new_password"]

    cached_otp = cache.get(f"password_reset_{email}")
    if not cached_otp or cached_otp != otp:
        return Response(
            {"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user.password = make_password(new_password)
    user.save()
    cache.delete(f"password_reset_{email}")
    return Response({"message": "Password has been reset successfully"})


@api_view(["POST"])
def resend_otp(request):
    class PasswordResetRequestSerializer(serializers.Serializer):
        email = serializers.EmailField()

    serializer = PasswordResetRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    email = serializer.validated_data["email"]
    user = User.objects.filter(email=email).first()
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    otp = generate_otp()
    cache.set(f"password_reset_{email}", otp, timeout=180)
    send_reset_email(user, otp)

    return Response({"message": "New OTP sent to email"})


###################### Change Driver Status ################################
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from ..models import User


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_driver_status(request, driver_id):
    """
    Update the driver's status using the driver ID passed in the URL.
    Only a driver can update their own status.
    """
    try:
        driver = User.objects.get(id=driver_id, type=User.UserType.DRIVER)
    except User.DoesNotExist:
        return Response(
            {"error": "Driver not found or user is not a driver"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Optional: Ensure the authenticated user is updating their own status.
    # Remove or adjust this check if your authentication logic differs.
    if request.user.id != driver.id:
        return Response(
            {"error": "You can only update your own status."},
            status=status.HTTP_403_FORBIDDEN,
        )

    new_status = request.data.get("driver_status")
    if new_status not in dict(User.DriverStatus.choices):
        return Response(
            {"error": "Invalid status provided. Choose online, offline, or busy."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    driver.driver_status = new_status
    driver.save()

    return Response(
        {
            "message": "Driver status updated successfully.",
            "driver_id": driver.id,
            "driver_status": driver.driver_status,
        },
        status=status.HTTP_200_OK,
    )


################## Login With Google Api ################################
from ..models import Complaint
from ..serializer import ComplaintSerializer


@api_view(["GET", "POST"])
def complaint_list_create(request):
    if request.method == "GET":
        complaints = Complaint.objects.all().order_by("-created_at")
        serializer = ComplaintSerializer(complaints, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == "POST":
        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"error": f"User with id {user_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ComplaintSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


################## Login With Google Api ################################
# # drivers/views.py
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth import get_user_model, login
# from allauth.socialaccount.models import SocialAccount
# from allauth.socialaccount.helpers import complete_social_login
# from allauth.socialaccount import app_settings as allauth_settings

# # Import Google verification utilities (install via pip install google-auth)
# from google.oauth2 import id_token as google_id_token
# from google.auth.transport import requests as google_requests


# # You can also use DRF’s APIView if you prefer. Here we use a simple function view.
# @api_view(["POST"])
# def google_login(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "POST request required"}, status=400)

#     try:
#         data = json.loads(request.body.decode("utf-8"))
#     except Exception:
#         return JsonResponse({"error": "Invalid JSON"}, status=400)

#     access_token = data.get("access_token")
#     if not access_token:
#         return JsonResponse({"error": "access_token not provided"}, status=400)

#     # Verify the access token using Google's library.
#     try:
#         # Use your Google client_id from settings (or hardcode here)
#         from django.conf import settings

#         client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"]
#         id_info = google_id_token.verify_oauth2_token(
#             access_token, google_requests.Request(), client_id
#         )
#     except Exception as e:
#         return JsonResponse({"error": "Invalid token: " + str(e)}, status=400)

#     email = id_info.get("email")
#     if not email:
#         return JsonResponse({"error": "No email found in token"}, status=400)

#     # Get or create the user
#     User = get_user_model()
#     user, created = User.objects.get_or_create(
#         email=email, defaults={"username": email}
#     )

#     # (Optional) Create or update the SocialAccount record for audit.
#     social_account, _ = SocialAccount.objects.get_or_create(
#         user=user, provider="google", defaults={"extra_data": id_info}
#     )
#     # Update extra_data if needed.
#     if not created:
#         social_account.extra_data = id_info
#         social_account.save()

#     # Log the user in (optional; for an API you may wish instead to return a token)
#     login(request, user)

#     # Return a success response. In a full solution you might return a JWT.
#     return JsonResponse({"detail": "Successfully logged in", "email": email})
