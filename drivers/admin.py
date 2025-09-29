from django.contrib import admin
from django.db.models import Sum  # for aggregation
from .models import User, Car, DriveInformationLicense, Trip, Complaint
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register the User model
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "phone", "type", "last_login")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email", "phone")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
        (("User Type"), {"fields": ("type",)}),
    )
    list_filter = ("type", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")


class DriveInformationResource(resources.ModelResource):
    class Meta:
        model = DriveInformationLicense
        fields = tuple(f.name for f in DriveInformationLicense._meta.get_fields())


class DriveInformationLicenseAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [DriveInformationResource]
    list_filter = ["first_name", "blood_type"]


class ComplaintResource(resources.ModelResource):
    class Meta:
        model = Complaint
        fields = tuple(f.name for f in Complaint._meta.get_fields())


class ComplaintAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [ComplaintResource]
    list_filter = ["user", "phone"]


class TripResource(resources.ModelResource):
    class Meta:
        model = Complaint
        fields = tuple(f.name for f in Trip._meta.get_fields())


class TriptAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [TripResource]
    list_filter = [
        "client",
        "driver",
        "status",
        "driver",
        "payment_method",
        "payment_status",
    ]


class CarResource(resources.ModelResource):
    class Meta:
        model = Complaint
        fields = tuple(f.name for f in Car._meta.get_fields())


class CarAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    resource_classes = [CarResource]
    list_filter = ["driver", "car_number"]


# Register other models
admin.site.register(Car, CarAdmin)
admin.site.register(DriveInformationLicense, DriveInformationLicenseAdmin)
admin.site.register(Trip, TriptAdmin)
admin.site.register(Complaint, ComplaintAdmin)
# admin.site.register(Rating)
