from decimal import Decimal
from enum import Enum


# Constants for the cutting technique model
REACTIVATE_CUTTING = "reactivate_cutting"
DEACTIVATE_CUTTING = "deactivate_cutting"
NO_CHANGE_CUTTING = "no_change_cutting"


class CategoryMaterialDataProperties(Enum):
    """Define the data properties of a category material."""

    MODEL_NAME = "materialcategory"
    NAME_MAX_LENGTH = 50
    DESCRIPTION_MAX_LENGTH = 500


CATEGORY_MATERIAL_MODEL = CategoryMaterialDataProperties.MODEL_NAME.value


class MaterialsDataProperties(Enum):
    """Define the data properties of a material."""

    SECTION_DESCRIPTIONS = "descriptions"
    SECTION_BASE = "base_info"
    SECTION_IMAGES = "images"
    SECTION_THICKNESS = "thicknesses"
    MODEL_NAME = "material"
    BASE_FIELDS = [
        "code",
        "name",
        "category__code",
        "is_active",
    ]
    IMAGE_FIELDS = [
        "banner_image",
        "description_image",
        "about_image",
        "uses_image",
        "texture_image",
    ]
    DESCRIP_FIELDS = [
        "description_text",
        "about_text",
        "common_uses_text",
        "features_highlights",
    ]
    NAME_MAX_LENGTH = 50
    DESCRIPTION_MAX_LENGTH = 500
    ABOUT_MAX_LENGTH = 500
    COMMON_USES_MAX_LENGTH = 500
    URL_MAX_LENGTH = 2083


MATERIAL_MODEL = MaterialsDataProperties.MODEL_NAME.value


class ThicknessDataProperties(Enum):
    """Define the data properties of a thickness."""

    MODEL_NAME = "thicknessmaterial"
    MAX_DIGITS = 4
    DECIMAL_PLACES = 2
    MAX_VALUE = Decimal(99.99)
    MIN_VALUE = Decimal(0.01)


THICKNESS_MODEL = ThicknessDataProperties.MODEL_NAME.value


class CutDataProperties(Enum):
    """Define the data properties of a cutting technique."""

    SECTION_DESCRIPTIONS = "descriptions"
    SECTION_BASE = "base_info"
    SECTION_IMAGES = "images"
    BASE_FIELDS = [
        "code",
        "name",
        "is_active",
    ]
    IMAGE_FIELDS = [
        "banner_image",
        "main_image",
        "card_image",
        "about_image",
        "uses_image",
    ]
    DESCRIP_FIELDS = [
        "about_text",
        "common_uses_text",
        "main_text",
        "card_text",
    ]
    MODEL_NAME = "cuttingtechnique"
    NAME_MAX_LENGTH = 50
    ABOUT_MAX_LENGTH = 500
    COMMON_USES_MAX_LENGTH = 500
    MAIN_TEXT_MAX_LENGTH = 500
    CARD_TEXT_MAX_LENGTH = 250
    URL_MAX_LENGTH = 2083


CUTTING_TECHNIQUE_MODEL = CutDataProperties.MODEL_NAME.value


STATIC_INFO_PERMISSIONS = {
    "add_cuttingtechnique": f"dashboard.add_{CUTTING_TECHNIQUE_MODEL}",
    "view_cuttingtechnique": f"dashboard.view_{CUTTING_TECHNIQUE_MODEL}",
    "change_cuttingtechnique": f"dashboard.change_{CUTTING_TECHNIQUE_MODEL}",
    "activate_cuttingtechnique": f"dashboard.activate_{CUTTING_TECHNIQUE_MODEL}",
    "deactivate_cuttingtechnique": f"dashboard.deactivate_{CUTTING_TECHNIQUE_MODEL}",
    "delete_cuttingtechnique": f"dashboard.delete_{CUTTING_TECHNIQUE_MODEL}",
    "add_material": f"dashboard.add_{MATERIAL_MODEL}",
    "view_material": f"dashboard.view_{MATERIAL_MODEL}",
    "change_material": f"dashboard.change_{MATERIAL_MODEL}",
    "activate_material": f"dashboard.activate_{MATERIAL_MODEL}",
    "deactivate_material": f"dashboard.deactivate_{MATERIAL_MODEL}",
    "delete_material": f"dashboard.delete_{MATERIAL_MODEL}",
    "add_thickness": f"dashboard.add_{THICKNESS_MODEL}",
    "change_thickness": f"dashboard.change_{THICKNESS_MODEL}",
    "delete_thickness": f"dashboard.delete_{THICKNESS_MODEL}",
}
