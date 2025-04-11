from apps.users.infrastructure.serializers import RegisterBaseUserSerializer
from apps.users.domain.constants import CompanyDataProperties, COMPANY_MODEL
from apps.users.domain.interfaces import IUserRepository
from apps.utils import ERROR_MESSAGES
from rest_framework import serializers
from django.core.validators import RegexValidator
from phonenumbers import PhoneNumberFormat, PhoneNumber, parse, format_number
from phonenumber_field.serializerfields import PhoneNumberField
from typing import Dict, Any


# Company properties
NAME_MAX_LENGTH = CompanyDataProperties.NAME_MAX_LENGTH.value
RUC_MAX_LENGTH = CompanyDataProperties.RUC_MAX_LENGTH.value
PHONE_NUMBER_MAX_LENGTH = CompanyDataProperties.PHONE_NUMBER_MAX_LENGTH.value
ADDRESS_MAX_LENGTH = CompanyDataProperties.ADDRESS_MAX_LENGTH.value


class CompanyRoleSerializer(serializers.Serializer):
    """Defines the fields that are required for the company user profile."""

    name = serializers.CharField(
        required=True,
        max_length=NAME_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )
    ruc = serializers.CharField(
        required=True,
        max_length=RUC_MAX_LENGTH,
        min_length=RUC_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
            "min_length": ERROR_MESSAGES["min_length"],
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

    def validate_name(self, value: str) -> str:
        """Validate that the name is not in use."""

        exists = self.__user_repository.exists(
            model_name=COMPANY_MODEL,
            data={"name": value},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["first_name_in_use"],
            )

        return value

    def validate_ruc(self, value: str) -> str:
        """Validate that the identification number is not in use."""

        exists = self.__user_repository.exists(
            model_name=COMPANY_MODEL,
            data={"ruc": value},
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
            numobj=numobj,
            num_format=PhoneNumberFormat.E164,
        )

        exists = self.__user_repository.exists(
            model_name=COMPANY_MODEL,
            data={"phone_number": formatted_number},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["phone_in_use"],
            )

        return formatted_number

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

        return attrs


class RegisterCompanySerializer(CompanyRoleSerializer, RegisterBaseUserSerializer):
    """Defines the fields that are required for the company user registration."""

    def __init__(self, user_repository: IUserRepository, *args, **kwargs) -> None:
        super().__init__(user_repository=user_repository, *args, **kwargs)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:

        attrs = super().validate(attrs)

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
