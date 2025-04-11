from apps.dashboard import models
from django.contrib import admin


@admin.register(models.MaterialCategory)
class MaterialCategoryAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the `MaterialCategory` model."""

    list_display = [
        "id",
        "name",
        "code",
        "description_text",
        "is_active",
        "date_joined",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "code"]
    readonly_fields = ["date_joined"]


@admin.register(models.Material)
class MaterialAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the Material model."""

    list_display = [
        "id",
        "name",
        "code",
        "category",
        "description_text",
        "about_text",
        "common_uses_text",
        "banner_image",
        "description_image",
        "about_image",
        "uses_image",
        "texture_image",
        "features_highlights",
        "is_active",
        "date_joined",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "code", "category"]
    readonly_fields = ["date_joined"]


@admin.register(models.ThicknessMaterial)
class ThicknessMaterialAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the ThicknessMaterial model."""

    list_display = [
        "id",
        "material",
        "value",
        "compatibility_cut",
    ]
    search_fields = ["material"]


@admin.register(models.CuttingTechnique)
class CuttingTechniqueAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the CuttingTechnique model."""

    list_display = [
        "id",
        "name",
        "code",
        "about_text",
        "card_text",
        "common_uses_text",
        "main_text",
        "banner_image",
        "card_image",
        "main_image",
        "about_image",
        "uses_image",
        "is_active",
        "date_joined",
    ]
    list_filter = ["is_active"]
    search_fields = ["name", "code"]
    readonly_fields = ["date_joined"]


@admin.register(models.UsesCuts)
class UsesCutsAdminPanel(admin.ModelAdmin):
    """Admin panel configuration for the UsesCuts model."""

    list_display = [
        "id",
        "cut",
        "number_uses",
    ]
    search_fields = ["cut"]
