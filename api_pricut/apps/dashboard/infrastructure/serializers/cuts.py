from apps.dashboard.domain.interfaces import IStaticInfoRepository
from apps.dashboard.domain.constants import CutDataProperties
from apps.dashboard.domain.entities import CuttingTechnique
from apps.utils import ERROR_MESSAGES
from rest_framework import serializers
from django.db.models import QuerySet
from typing import Dict, List, Any


class CutBaseInfoSerializer(serializers.Serializer):
    """Defines the fields of the 'base info' section of a cutting technique."""

    name = serializers.CharField(
        required=True,
        max_length=CutDataProperties.NAME_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
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

    def validate_name(self, value: str) -> str:
        """Validate that the name does not exist in the database."""

        exists = self.__static_info_repository.exists(
            data={"name": value},
            data_type="cut",
        )

        if exists:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["cut_exists"],
            )

        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        # Validate the data provided in the request body
        if self.partial:
            if len(attrs) == 0:
                raise serializers.ValidationError(
                    code="invalid_data",
                    detail=ERROR_MESSAGES["empty"],
                )

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


class CutDescriptionSerializer(serializers.Serializer):
    """Defines the fields of the 'descriptions' section of a cutting technique."""

    about_text = serializers.CharField(
        required=True,
        max_length=CutDataProperties.ABOUT_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    card_text = serializers.CharField(
        required=True,
        max_length=CutDataProperties.CARD_TEXT_MAX_LENGTH.value,
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
        max_length=CutDataProperties.COMMON_USES_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    main_text = serializers.CharField(
        required=True,
        max_length=CutDataProperties.MAIN_TEXT_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        # Validate the data provided in the request body
        if self.partial:
            if len(attrs) == 0:
                raise serializers.ValidationError(
                    code="invalid_data",
                    detail=ERROR_MESSAGES["empty"],
                )

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


class CutImagesSerializer(serializers.Serializer):
    """Defines the fields of the 'images' section of a cutting technique."""

    banner_image = serializers.URLField(
        required=True,
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    card_image = serializers.URLField(
        required=True,
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    main_image = serializers.URLField(
        required=True,
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
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
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
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
        max_length=CutDataProperties.URL_MAX_LENGTH.value,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid_url"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        # Validate the data provided in the request body
        if self.partial:
            if len(attrs) == 0:
                raise serializers.ValidationError(
                    code="invalid_data",
                    detail=ERROR_MESSAGES["empty"],
                )

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


class CutSerializer(
    CutBaseInfoSerializer,
    CutDescriptionSerializer,
    CutImagesSerializer,
):
    """Defines the data fields of a cutting technique."""

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            static_info_repository=static_info_repository,
            *args,
            **kwargs,
        )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the data provided in the request body."""

        # Validate the data provided in the request body
        if self.partial:
            if len(attrs) == 0:
                raise serializers.ValidationError(
                    code="invalid_data",
                    detail=ERROR_MESSAGES["empty"],
                )

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


class CutBaseInfoReadOnlySerializer(serializers.Serializer):
    """Serializer for the base information of a cut."""

    name = serializers.CharField(read_only=True)
    code = serializers.CharField(read_only=True)


class CutDescriptionReadOnlySerializer(serializers.Serializer):
    """Serializer for the descriptions of a cut."""

    about_text = serializers.CharField(read_only=True)
    common_uses_text = serializers.CharField(read_only=True)
    main_text = serializers.CharField(read_only=True)
    card_text = serializers.CharField(read_only=True)


class CutImagesReadOnlySerializer(serializers.Serializer):
    """Serializer for the images of a cut."""

    banner_image = serializers.URLField(read_only=True)
    main_image = serializers.URLField(read_only=True)
    card_image = serializers.URLField(read_only=True)
    about_image = serializers.URLField(read_only=True)
    uses_image = serializers.URLField(read_only=True)


class CutReadOnlySerializer(serializers.Serializer):
    """
    Serializer for the CuttingTechniques model.

    This serializer is used to convert CuttingTechniques model instances into
    a JSON representation. It includes fields for cutting technique details
    and related cutting capacity information.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.base_info_serializer = CutBaseInfoReadOnlySerializer()
        self.descriptions_serializer = CutDescriptionReadOnlySerializer()
        self.images_serializer = CutImagesReadOnlySerializer()

    def to_representation(
        self,
        many: bool,
        data: QuerySet[CuttingTechnique] | CuttingTechnique,
    ) -> Dict[str, Any] | List[Dict[str, Any]]:
        """
        Convert a queryset of CuttingTechniques instances into a list of
        dictionaries.
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
            # fmt: on

            return response_data

        response_data: List[Dict[str, Any]] = []

        for cut in data:
            item = {}

            # fmt: off
            item["base_info"] = (
                self.base_info_serializer.to_representation(instance=cut)
            )
            item["descriptions"] = (
                self.descriptions_serializer.to_representation(instance=cut)
            )
            item["images"] = (
                self.images_serializer.to_representation(instance=cut)
            )
            # fmt: on

            response_data.append(item)

        return response_data
