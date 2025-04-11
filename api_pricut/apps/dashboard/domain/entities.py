from .constants import (
    CategoryMaterialDataProperties,
    MaterialsDataProperties,
    ThicknessDataProperties,
    CutDataProperties,
)
from django.db import models


class MaterialCategory(models.Model):
    """
    Represents a category of materials. It is used to categorize and manage
    different types of materials in the system.
    """

    id = models.AutoField(
        db_column="id",
        primary_key=True,
    )
    code = models.CharField(
        db_column="code",
        max_length=20,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        db_column="name",
        max_length=CategoryMaterialDataProperties.NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    description_text = models.CharField(
        db_column="description_text",
        max_length=CategoryMaterialDataProperties.DESCRIPTION_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        db_column="is_active",
        null=False,
        blank=False,
        db_index=True,
        default=False,
    )
    date_joined = models.DateTimeField(
        db_column="date_joined",
        auto_now_add=True,
    )

    class Meta:
        db_table = "dashboard.material_categories"
        verbose_name = "Material category"
        verbose_name_plural = "Material categories"

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.name


class Material(models.Model):
    """
    Represents a material used in various applications. It is used to
    categorize and manage different types of materials in the system.
    """

    id = models.AutoField(
        db_column="id",
        primary_key=True,
    )
    code = models.CharField(
        db_column="code",
        max_length=MaterialsDataProperties.NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        db_column="name",
        max_length=MaterialsDataProperties.NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    category = models.ForeignKey(
        db_column="category",
        to="MaterialCategory",
        to_field="id",
        on_delete=models.SET_NULL,
        null=True,
    )
    description_text = models.CharField(
        db_column="description_text",
        max_length=MaterialsDataProperties.DESCRIPTION_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    about_text = models.CharField(
        db_column="about_text",
        max_length=MaterialsDataProperties.ABOUT_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    common_uses_text = models.CharField(
        db_column="common_uses_text",
        max_length=MaterialsDataProperties.COMMON_USES_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    banner_image = models.URLField(
        db_column="banner_image",
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    description_image = models.URLField(
        db_column="description_image",
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    about_image = models.URLField(
        db_column="about_image",
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    uses_image = models.URLField(
        db_column="uses_image",
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    texture_image = models.URLField(
        db_column="texture_image",
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    features_highlights = models.JSONField(
        db_column="features_highlights",
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        db_column="is_active",
        null=False,
        blank=False,
        db_index=True,
        default=False,
    )
    date_joined = models.DateTimeField(
        db_column="date_joined",
        auto_now_add=True,
    )

    class Meta:
        db_table = "dashboard.materials"
        verbose_name = "Material"
        verbose_name_plural = "Materials"
        permissions = [
            ("activate_material", "Can activate a material"),
            ("deactivate_material", "Can deactivate a material"),
        ]

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.name


class ThicknessMaterial(models.Model):
    """
    Represents the thickness of a material.

    This model includes information about the thickness value and its
    compatibility with different cutting techniques. It is used to manage
    and categorize material thicknesses in the system.
    """

    id = models.IntegerField(
        db_column="id",
        primary_key=True,
    )
    material = models.ForeignKey(
        db_column="material",
        to="Material",
        to_field="id",
        related_name="thicknesses",
        on_delete=models.SET_NULL,
        null=True,
    )
    value = models.DecimalField(
        db_column="value",
        max_digits=ThicknessDataProperties.MAX_DIGITS.value,
        decimal_places=ThicknessDataProperties.DECIMAL_PLACES.value,
        null=False,
        blank=False,
    )
    compatibility_cut = models.JSONField(
        db_column="compatibility_cut",
        default=dict,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = "dashboard.thicknesses_materials"
        verbose_name = "Thickness material"
        verbose_name_plural = "Thicknesses materials"

    def save(self, *args, **kwargs) -> None:
        if not self.id:
            data = ThicknessMaterial.objects.aggregate(models.Max("id"))
            max_id = data["id__max"]
            self.id = max_id + 1

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return str(self.value)


class CuttingTechnique(models.Model):
    """
    Represents a cutting technique used in material processing. It is used
    to manage and categorize different cutting techniques in the system.
    """

    id = models.AutoField(
        db_column="id",
        primary_key=True,
    )
    code = models.CharField(
        db_column="code",
        max_length=CutDataProperties.NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    name = models.CharField(
        db_column="name",
        max_length=CutDataProperties.NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
        unique=True,
        db_index=True,
    )
    about_text = models.CharField(
        db_column="about_text",
        max_length=CutDataProperties.ABOUT_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    common_uses_text = models.CharField(
        db_column="common_uses_text",
        max_length=CutDataProperties.COMMON_USES_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    main_text = models.CharField(
        db_column="main_text",
        max_length=CutDataProperties.MAIN_TEXT_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    card_text = models.CharField(
        db_column="card_text",
        max_length=CutDataProperties.CARD_TEXT_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    banner_image = models.URLField(
        db_column="banner_image",
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    main_image = models.URLField(
        db_column="main_image",
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    card_image = models.URLField(
        db_column="card_image",
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    about_image = models.URLField(
        db_column="about_image",
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    uses_image = models.URLField(
        db_column="uses_image",
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        db_column="is_active",
        null=False,
        blank=False,
        db_index=True,
        default=False,
    )
    date_joined = models.DateTimeField(
        db_column="date_joined",
        auto_now_add=True,
    )

    class Meta:
        db_table = "dashboard.cutting_techniques"
        verbose_name = "Cutting Technique"
        verbose_name_plural = "Cutting Techniques"
        permissions = [
            ("activate_cuttingtechnique", "Can activate cutting technique"),
            ("deactivate_cuttingtechnique", "Can deactivate cutting"),
        ]

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.name


class UsesCuts(models.Model):
    """
    This model is responsible for tracking the number of times a cutting technique
    is used for a material in its different thicknesses. This will help determine
    when a cutting service should be deactivated or reactivated.
    """

    id = models.AutoField(
        db_column="id",
        primary_key=True,
    )
    cut = models.OneToOneField(
        db_column="cut",
        to="CuttingTechnique",
        to_field="id",
        on_delete=models.SET_NULL,
        null=True,
    )
    number_uses = models.IntegerField(
        db_column="number_uses",
        null=False,
        blank=False,
    )

    class Meta:
        db_table = "dashboard.uses_cuts"
        verbose_name = "Use cut"
        verbose_name_plural = "Uses cuts"
