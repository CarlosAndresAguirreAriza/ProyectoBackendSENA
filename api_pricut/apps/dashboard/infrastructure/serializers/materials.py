from apps.dashboard.domain.interfaces import IStaticInfoRepository
from apps.dashboard.domain.constants import (
    CategoryMaterialDataProperties,
    MaterialsDataProperties,
    ThicknessDataProperties,
)
from apps.dashboard.domain.entities import ThicknessMaterial, Material
from apps.utils import ERROR_MESSAGES
from rest_framework import serializers
from django.core.validators import URLValidator, RegexValidator
from django.db.models import QuerySet
from typing import List, Dict, Any


class ThicknessSerializer(serializers.Serializer):
    """Defines the fields that are required for thickness data."""

    id = serializers.IntegerField(
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
        },
    )
    value = serializers.DecimalField(
        required=True,
        max_digits=ThicknessDataProperties.MAX_DIGITS.value,
        decimal_places=ThicknessDataProperties.DECIMAL_PLACES.value,
        max_value=ThicknessDataProperties.MAX_VALUE.value,
        min_value=ThicknessDataProperties.MIN_VALUE.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_digits": ERROR_MESSAGES["max_digits"],
            "decimal_places": ERROR_MESSAGES["decimal_places"],
            "max_whole_digits": ERROR_MESSAGES["max_whole_digits"],
            "max_value": ERROR_MESSAGES["max_value"],
            "min_value": ERROR_MESSAGES["min_value"],
        },
    )
    compatibility_cut = serializers.DictField(
        required=True,
        allow_empty=False,
        child=serializers.BooleanField(
            error_messages={
                "null": ERROR_MESSAGES["null"],
                "blank": ERROR_MESSAGES["blank"],
                "invalid": ERROR_MESSAGES["invalid"],
            },
        ),
        error_messages={
            "required": ERROR_MESSAGES["required"],
            "null": ERROR_MESSAGES["null"],
            "blank": ERROR_MESSAGES["blank"],
            "invalid": ERROR_MESSAGES["invalid"],
            "empty": ERROR_MESSAGES["empty"],
            "not_a_dict": ERROR_MESSAGES["not_a_dict"],
        },
    )

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__static_info_repository = static_info_repository

    def validate_compatibility_cut(
        self, value: Dict[str, bool]
    ) -> Dict[str, bool]:
        """Validate compatibility with cutting techniques."""

        cutting_codes = list(value.keys())
        cuts = self.__static_info_repository.get_cut(
            filters={"is_active__in": [True, False]},
            section="base_info",
        )
        cuts_codes = [cut.code for cut in cuts]

        # Validate that the cutting techniques exist in the database
        for code in cutting_codes:
            if code not in cuts_codes:
                detail = ERROR_MESSAGES["cut_not_exist"].format(cut_code=code)

                raise serializers.ValidationError(
                    code="invalid_data",
                    detail=detail,
                )

        # Check if all dictionary values are False
        if all(not v for v in value.values()):
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["compatibility_cut"],
            )

        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        # Validate the data provided in the request body
        unknown_fields = set(self.initial_data) - set(self.fields)

        if unknown_fields:
            raise serializers.ValidationError(
                code="invalid_data",
                detail={
                    field: ERROR_MESSAGES["invalid_field"]
                    for field in unknown_fields
                },
            )

        return attrs


class CreateThicknessSerializer(ThicknessSerializer):
    """Defines the fields that are necessary to create a new thickness."""

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        data: Dict[str, Any] = {},
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            static_info_repository=static_info_repository,
            data=data,
            *args,
            **kwargs,
        )
        self.fields.pop("id")


class UpdateThicknessSerializer(ThicknessSerializer):
    """Defines the fields that are necessary to update the data of a thickness."""

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        data: Dict[str, Any] = {},
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            static_info_repository=static_info_repository,
            data=data,
            *args,
            **kwargs,
        )
        id = self.fields["id"]
        id.required = True


class ThicknessReadOnlySerializer(serializers.Serializer):
    """
    Serializer for the Thicknesses model.

    This serializer is used to convert Thicknesses model instances into
    a JSON representation. It includes fields for the thickness value
    and its compatibility with different cutting techniques.
    """

    id = serializers.IntegerField(read_only=True)
    value = serializers.DecimalField(
        read_only=True,
        max_digits=4,
        decimal_places=2,
    )
    compatibility_cut = serializers.DictField(read_only=True)

    def to_representation(
        self,
        many: bool,
        data: QuerySet[ThicknessMaterial] | ThicknessMaterial,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """
        Convert a queryset of Thicknesses instances into a list of dictionaries.

        #### Parameters:
            - data: the queryset of `ThicknessMaterial` instances.
            - many: a boolean value that indicates if the queryset contains
            multiple instances.
        """

        if not many:
            return super().to_representation(instance=data)

        response_data = []

        for thickness in data:
            response_data.append(super().to_representation(instance=thickness))

        return response_data


class MaterialSerializer(serializers.Serializer):
    """Defines the fields that are required for material data."""

    name = serializers.CharField(
        required=True,
        max_length=MaterialsDataProperties.NAME_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    category = serializers.CharField(
        required=True,
        max_length=CategoryMaterialDataProperties.NAME_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    description_text = serializers.CharField(
        required=True,
        max_length=MaterialsDataProperties.DESCRIPTION_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    about_text = serializers.CharField(
        required=True,
        max_length=MaterialsDataProperties.ABOUT_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    common_uses_text = serializers.CharField(
        required=True,
        max_length=MaterialsDataProperties.COMMON_USES_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    banner_image = serializers.URLField(
        required=True,
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    description_image = serializers.URLField(
        required=True,
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    about_image = serializers.URLField(
        required=True,
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    uses_image = serializers.URLField(
        required=True,
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    texture_image = serializers.URLField(
        required=True,
        max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    features_highlights = serializers.ListField(
        child=serializers.DictField(
            required=True,
            allow_empty=False,
            child=serializers.CharField(
                max_length=MaterialsDataProperties.URL_MAX_LENGTH.value,
                error_messages={
                    "invalid": ERROR_MESSAGES["invalid"],
                    "required": ERROR_MESSAGES["required"],
                    "blank": ERROR_MESSAGES["blank"],
                    "null": ERROR_MESSAGES["null"],
                    "max_length": ERROR_MESSAGES["max_length"],
                },
            ),
        ),
        required=True,
        max_length=10,
        min_length=1,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length_list"],
            "min_length": ERROR_MESSAGES["min_length_list"],
        },
    )

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.__static_info_repository = static_info_repository

    def validate_category(self, value: str) -> str:
        """Validate that the material category exists in the database."""

        exists = self.__static_info_repository.exists(
            data_type="category_material",
            data={"code": value},
        )

        if not exists:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["category_not_exist"],
            )

        return value

    def validate_name(self, value: str) -> str:
        """Validate that the name does not exist in the database."""

        exists = self.__static_info_repository.exists(
            data_type="material",
            data={"name": value},
        )

        if exists:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["material_exists"],
            )

        return value

    def validate_features_highlights(
        self, value: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Validate features and highlights."""

        try:
            titles = [item["title"] for item in value]
            images = [item["image"] for item in value]
        except KeyError:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["features_highlights"],
            )

        for image in images:
            validator = URLValidator(
                message={"image": ERROR_MESSAGES["invalid_url"]}
            )
            validator(value=image)

        for title in titles:
            validator = RegexValidator(
                regex=r"^[A-Z][a-zA-Z0-9 .,!?]{1,50}$",
                message={"title": ERROR_MESSAGES["invalid"]},
            )
            validator(value=title)

        return value


class UpdateMaterialSerializer(MaterialSerializer):
    """Defines the fields that are necessary to update the data of a material."""

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        data: Dict[str, Any] = {},
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            static_info_repository=static_info_repository,
            data=data,
            *args,
            **kwargs,
        )
        self.fields["thicknesses"] = serializers.ListField(
            child=UpdateThicknessSerializer(),
            min_length=1,
            required=True,
            allow_empty=False,
            error_messages={
                "invalid": ERROR_MESSAGES["invalid"],
                "required": ERROR_MESSAGES["required"],
                "blank": ERROR_MESSAGES["blank"],
                "null": ERROR_MESSAGES["null"],
                "empty": ERROR_MESSAGES["empty"],
                "min_length": ERROR_MESSAGES["min_length_list"],
            },
        )
        self.fields.pop("texture_image")
        self.fields.pop("uses_image")
        self.fields.pop("about_image")
        self.fields.pop("description_image")
        self.fields.pop("banner_image")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        unknown_fields = set(self.initial_data) - set(self.fields)

        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not allowed." for field in unknown_fields}
            )

        return attrs


class MaterialBaseInfoReadOnlySerializer(serializers.Serializer):
    """Serializer for the base information of a material."""

    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)


class MaterialDescriptionsReadOnlySerializer(serializers.Serializer):
    """Serializer for the descriptions of a material."""

    description_text = serializers.CharField(read_only=True)
    about_text = serializers.CharField(read_only=True)
    common_uses_text = serializers.CharField(read_only=True)
    features_highlights = serializers.ListField(
        child=serializers.DictField(
            child=serializers.URLField(read_only=True),
            read_only=True,
        ),
        read_only=True,
    )


class MaterialImagesReadOnlySerializer(serializers.Serializer):
    """Serializer for the images of a material."""

    banner_image = serializers.URLField(read_only=True)
    description_image = serializers.URLField(read_only=True)
    about_image = serializers.URLField(read_only=True)
    uses_image = serializers.URLField(read_only=True)
    texture_image = serializers.URLField(read_only=True)


class MaterialReadOnlySerializer(serializers.Serializer):
    """
    Serializer for the Materials model.

    This serializer is used to convert Materials model instances into
    a JSON representation. It includes fields for material details and
    related thickness cutting information.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.thickness_serializer = ThicknessReadOnlySerializer()
        self.base_info_serializer = MaterialBaseInfoReadOnlySerializer()
        self.descriptions_serializer = MaterialDescriptionsReadOnlySerializer()
        self.images_serializer = MaterialImagesReadOnlySerializer()

    def to_representation(
        self,
        many: bool,
        data: QuerySet[Material] | Material,
    ) -> List[Dict[str, Any]] | Dict[str, Any]:
        """
        Convert a queryset of Materials instances into a list of dictionaries.

        #### Parameters:
            - data: the queryset of `Material` instances.
            - many: a boolean value that indicates if the queryset contains
            multiple instances.
        """

        if not many:
            response_data = {}

            # fmt: off
            response_data["base_info"] = (
                self.base_info_serializer.to_representation(instance=data)
            )
            response_data["descriptions"] = (
                self.descriptions_serializer.to_representation(instance=data)
            )
            response_data["images"] = (
                self.images_serializer.to_representation(instance=data)
            )
            response_data["thicknesses"] = (
                self.thickness_serializer.to_representation(
                    data=data.thicknesses.all(),
                    many=True,
                )
            )
            # fmt: on

            return response_data

        response_data: List[Dict[str, Any]] = []

        for material in data:
            item = {}

            # fmt: off
            item["base_info"] = (
                self.base_info_serializer.to_representation(instance=material)
            )
            item["descriptions"] = (
                self.descriptions_serializer.to_representation(instance=material)
            )
            item["images"] = (
                self.images_serializer.to_representation(instance=material)
            )
            item["thicknesses"] = (
                self.thickness_serializer.to_representation(
                    data=material.thicknesses.all(),
                    many=True,
                )
            )
            # fmt: on

            response_data.append(item)

        return response_data
