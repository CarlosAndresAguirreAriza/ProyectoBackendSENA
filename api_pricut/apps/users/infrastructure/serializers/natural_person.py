from apps.users.infrastructure.serializers import (
    BaseUserReadOnlySerializer,
    RegisterBaseUserSerializer,
)
from apps.users.domain.interfaces import IUserRepository
from apps.users.domain.constants import (
    NaturalPersonDataProperties,
    NATURAL_PERSON_MODEL,
    NATURAL_PERSON_ROLE,
)
from apps.users.models import User
from apps.utils import ERROR_MESSAGES
from rest_framework import serializers
from django.core.validators import RegexValidator
from phonenumbers import PhoneNumberFormat, PhoneNumber, parse, format_number
from phonenumber_field.serializerfields import PhoneNumberField
from typing import Dict, Any


# Natural person properties data
FIRST_NAME_MAX_LENGTH = NaturalPersonDataProperties.FIRST_NAME_MAX_LENGTH.value
LAST_NAME_MAX_LENGTH = NaturalPersonDataProperties.LAST_NAME_MAX_LENGTH.value
CC_MAX_LENGTH = NaturalPersonDataProperties.CC_MAX_LENGTH.value
PHONE_NUMBER_MAX_LENGTH = NaturalPersonDataProperties.PHONE_NUMBER_MAX_LENGTH.value
ADDRESS_MAX_LENGTH = NaturalPersonDataProperties.ADDRESS_MAX_LENGTH.value


class NaturalPersonRoleSerializer(serializers.Serializer):
    """Defines the data of a user with the natural person role"""

    first_name = serializers.CharField(
        required=True,
        max_length=FIRST_NAME_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
        validators=[
            RegexValidator(
                regex=r"^[A-Za-zñÑáéíóúÁÉÍÓÚ\s]+$",
                code="invalid_data",
                message=ERROR_MESSAGES["invalid"],
            ),
        ],
    )
    last_name = serializers.CharField(
        required=True,
        max_length=LAST_NAME_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
        validators=[
            RegexValidator(
                regex=r"^[A-Za-zñÑáéíóúÁÉÍÓÚ\s]+$",
                code="invalid_data",
                message=ERROR_MESSAGES["invalid"],
            ),
        ],
    )
    cc = serializers.CharField(
        required=True,
        max_length=CC_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
        validators=[
            RegexValidator(
                regex=r"^\d+$",
                code="invalid_data",
                message=ERROR_MESSAGES["invalid"],
            ),
        ],
    )
    phone_number = PhoneNumberField(
        required=True,
        max_length=PHONE_NUMBER_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    address = serializers.CharField(
        required=True,
        max_length=ADDRESS_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )

    def __init__(self, user_repository: IUserRepository, *args, **kwargs) -> None:
        super().__init__(user_repository=user_repository, *args, **kwargs)
        self.__user_repository = user_repository

    def validate_first_name(self, value: str) -> str:
        """Validate that the first name is not in use."""

        exists = self.__user_repository.exists(
            model_name=NATURAL_PERSON_MODEL,
            data={"first_name": value},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["first_name_in_use"],
            )

        return value

    def validate_last_name(self, value: str) -> str:
        """Validate that the last name is not in use."""

        exists = self.__user_repository.exists(
            model_name=NATURAL_PERSON_MODEL,
            data={"last_name": value},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["last_name_in_use"],
            )

        return value

    def validate_cc(self, value: str) -> str:
        """Validate that the identification number is not in use."""

        exists = self.__user_repository.exists(
            model_name=NATURAL_PERSON_MODEL,
            data={"cc": value},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["cc_ruc_in_use"],
            )

        return value

    def validate_phone_number(self, value: PhoneNumber) -> str:
        """Validate that the phone number is not in use."""

        numobj = parse(number=str(value))
        formatted_number = format_number(
            num_format=PhoneNumberFormat.E164,
            numobj=numobj,
        )
        exists = self.__user_repository.exists(
            model_name=NATURAL_PERSON_MODEL,
            data={"phone_number": formatted_number},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["phone_in_use"],
            )

        return formatted_number


class RegisterNaturalPersonRoleSerializer(NaturalPersonRoleSerializer):
    """Defines the fields of the natural person role for registration."""

    def __init__(self, user_repository: IUserRepository, *args, **kwargs) -> None:
        super().__init__(user_repository=user_repository, *args, **kwargs)
        self.fields.pop("cc")
        self.fields.pop("phone_number")
        self.fields.pop("address")


class NaturalPersonRoleReadOnlySerializer(serializers.Serializer):
    """Defines the fields of the natural person role for reading."""

    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    cc = serializers.CharField(read_only=True)
    phone_number = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)


class RegisterNaturalPersonSerializer(
    RegisterNaturalPersonRoleSerializer,
    RegisterBaseUserSerializer,
):
    """
    Define the mandatory fields for the registration of a natural person, requesting
    only the minimum information necessary to complete the registration process.
    """

    def __init__(self, user_repository: IUserRepository, *args, **kwargs) -> None:
        super().__init__(user_repository=user_repository, *args, **kwargs)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the request data before continuing."""

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

        # Validate that the password and confirm password match
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                code="invalid_data",
                detail={
                    "confirm_password": [
                        ERROR_MESSAGES["password_mismatch"],
                    ]
                },
            )

        return attrs


class NaturalPersonReadOnlySerializer(serializers.Serializer):
    """Defines the fields of the natural person information for reading."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.base_data = BaseUserReadOnlySerializer()
        self.role_data = NaturalPersonRoleReadOnlySerializer()

    def to_representation(self, instance: User) -> Dict[str, Dict[str, Any]]:
        """Return a dictionary with the serialized data."""

        base_data = self.base_data.to_representation(instance=instance)
        role_data = self.role_data.to_representation(
            instance=getattr(instance, NATURAL_PERSON_ROLE)
        )

        return {"base_data": base_data, "role_data": role_data}
