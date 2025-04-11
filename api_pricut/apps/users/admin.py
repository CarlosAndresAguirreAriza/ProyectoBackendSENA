from apps.users import models
from django.contrib import admin


@admin.register(models.User)
class UserAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the `User` model."""

    list_display = [
        "uuid",
        "email",
        "password",
        "role",
        "is_staff",
        "is_superuser",
        "is_active",
        "is_deleted",
        "deleted_at",
        "date_joined",
        "last_login",
    ]
    list_filter = ["is_active", "is_deleted"]
    search_fields = ["email", "uuid", "role"]
    readonly_fields = ["date_joined", "password", "is_superuser"]
    ordering = ["-date_joined"]


@admin.register(models.NaturalPersonRole)
class NaturalPersonRoleAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the `NaturalPersonRole` model."""

    list_display = [
        "uuid",
        "base_data",
        "first_name",
        "last_name",
        "cc",
        "phone_number",
        "address",
    ]
    search_fields = ["uuid", "base_data", "cc", "phone_number"]


@admin.register(models.CompanyRole)
class CompanyRoleAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the `CompanyRole` model."""

    list_display = [
        "uuid",
        "base_data",
        "name",
        "ruc",
        "phone_number",
        "address",
    ]
    search_fields = ["uuid", "base_data", "ruc", "phone_number"]


@admin.register(models.AdminRole)
class AdminRoleAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the `AdminRole` model."""

    list_display = [
        "uuid",
        "base_data",
        "first_name",
        "last_name",
    ]
    search_fields = ["uuid", "base_data"]
