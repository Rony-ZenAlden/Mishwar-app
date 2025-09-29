from django.urls import path
from .views import user_view, trip_view, trip2_view

urlpatterns = [
    # Test APIs
    path("", user_view.index),
    # User APIs
    path("api/users/", user_view.user_list_create),
    path("api/users/<int:pk>/", user_view.user_detail),
    # Change Driver Status
    path("change-driver-status/<int:driver_id>/", user_view.change_driver_status),
    # Change Password APIs
    path("password-reset/", user_view.password_reset_request),
    path("password-reset-verify/", user_view.password_reset_verify),
    path("resend-otp/", user_view.resend_otp),
    # Car APIs
    path("api/cars/", user_view.car_list_getAll),
    path("api/cars/<str:username>/", user_view.car_list_create),
    path("api/car/<int:pk>/", user_view.car_detail),
    # DriveInformationLicense APIs
    path("api/drive-info/", user_view.drive_information_list_get),
    path("api/drive-infos/<str:username>/", user_view.drive_information_list_create),
    path("api/drive-info/<int:pk>/", user_view.drive_information_detail),
    # Authentication APIs
    path("login/", user_view.user_login),
    path("nearby/", trip_view.getNearbyDrivers),
    path("update-driver-location/", trip_view.updateDriverLocation),
    # Client Location
    path("update-user-location/", trip_view.updateUserLocation),
    # Complaints Client
    path("complaints/", user_view.complaint_list_create),
    # Get All Trip For Every User
    path("api/my-trips/", trip2_view.my_trips_list),
    # Trip Apis
    path("trips/", trip2_view.trip_request_view, name="trip-request"),
    path("trips/<int:trip_id>/accept/", trip2_view.accept_trip, name="accept-trip"),
    path("trips/<int:trip_id>/", trip2_view.get_trip_details),
    path("trips/<int:trip_id>/arrived/", trip2_view.driver_arrived),
    path("trips/<int:trip_id>/complete/", trip2_view.complete_trip),
    # Payment Apis
    path(
        "trips/<int:trip_id>/select-payment/",
        trip2_view.select_payment_method,
        name="select-payment",
    ),
    path(
        "trips/<int:trip_id>/confirm-online-payment/",
        trip2_view.confirm_online_payment,
        name="confirm-online-payment",
    ),
    path(
        "trips/<int:trip_id>/confirm-cash-payment/",
        trip2_view.confirm_cash_payment,
        name="confirm-cash-payment",
    ),
    path("trips/<int:trip_id>/rate/", trip2_view.rate_trip, name="rate-trip"),
    path("driver/<int:driver_id>/details/", user_view.driver_details),
]
