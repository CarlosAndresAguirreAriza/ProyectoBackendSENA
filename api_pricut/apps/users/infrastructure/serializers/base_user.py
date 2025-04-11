from apps.users.domain.constants import BaseUserDataProperties, BASE_USER_MODEL
from apps.users.domain.interfaces import IUserRepository
from apps.utils import ERROR_MESSAGES
from rest_framework import serializers
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError


# Base user properties
EMAIL_MAX_LENGTH = BaseUserDataProperties.EMAIL_MAX_LENGTH.value
PASSWORD_MAX_LENGTH = BaseUserDataProperties.PASSWORD_MAX_LENGTH.value
PASSWORD_MIN_LENGTH = BaseUserDataProperties.PASSWORD_MIN_LENGTH.value


class BaseUserSerializer(serializers.Serializer):
    """Defines the base data of a user."""

    email = serializers.EmailField(
        required=True,
        max_length=EMAIL_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )

    def __init__(self, user_repository: IUserRepository, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__user_repository = user_repository

    def validate_email(self, value: str) -> str:
        """Validate that the email is not in use."""

        exists = self.__user_repository.exists(
            model_name=BASE_USER_MODEL,
            data={"email": value},
        )

        if exists is True:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["email_in_use"],
            )

        return value


class RegisterBaseUserSerializer(BaseUserSerializer):
    """Defines the base data of a user."""

    password = serializers.CharField(
        required=True,
        write_only=True,
        max_length=PASSWORD_MAX_LENGTH,
        min_length=PASSWORD_MIN_LENGTH,
        style={"input_type": "password"},
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
            "min_length": ERROR_MESSAGES["min_length"],
        },
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
        },
    )

    def __init__(self, user_repository: IUserRepository, *args, **kwargs) -> None:
        super().__init__(user_repository=user_repository, *args, **kwargs)

    def validate_password(self, value: str) -> str:
        """
        This method checks the password for compliance with various security
        requirements, which may include length, complexity, similarity to user
        attributes, and presence in lists of common passwords.
        """

        try:
            CommonPasswordValidator().validate(password=value)
        except ValidationError:
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["password_common"],
            )

        if value.isdigit():
            raise serializers.ValidationError(
                code="invalid_data",
                detail=ERROR_MESSAGES["password_no_upper_lower"],
            )

        return value


class BaseUserReadOnlySerializer(serializers.Serializer):
    """Defines the base data of a user for read only."""

    email = serializers.EmailField(read_only=True)
