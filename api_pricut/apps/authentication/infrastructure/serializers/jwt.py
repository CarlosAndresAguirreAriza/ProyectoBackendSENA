from apps.authentication.jwt import AccessToken, JWTErrorMessages
from apps.users.domain.constants import BaseUserDataProperties
from apps.exceptions import JWTAPIError
from apps.utils import ERROR_MESSAGES
from settings.environments.base import SIMPLE_JWT
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework import serializers
from jwt import decode, DecodeError, ExpiredSignatureError
from typing import Dict, Any


# User base data properties
EMAIL_MAX_LENGTH = BaseUserDataProperties.EMAIL_MAX_LENGTH.value
PASSWORD_MAX_LENGTH = BaseUserDataProperties.PASSWORD_MAX_LENGTH.value

# Error messages
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value
ACCESS_NOT_EXPIRED = JWTErrorMessages.ACCESS_NOT_EXPIRED.value


class JWTLoginSerializer(serializers.Serializer):
    """
    Handles the data for user authentication. Checks that the provided email and
    password meet the necessary requirements.
    """

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
    password = serializers.CharField(
        required=True,
        max_length=PASSWORD_MAX_LENGTH,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
            "max_length": ERROR_MESSAGES["max_length"],
        },
    )

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the request data before continuing."""

        # Validate the data provided in the request body
        unknown_fields = set(self.initial_data) - set(self.fields)

        if unknown_fields:
            raise serializers.ValidationError(
                code="invalid_data",
                detail={
                    field: "This field is not allowed." for field in unknown_fields
                },
            )

        return attrs


class JWTUpdateSerializer(serializers.Serializer):
    """Handles data to update access token of a user."""

    access_token = serializers.CharField(
        required=True,
        error_messages={
            "invalid": ERROR_MESSAGES["invalid"],
            "required": ERROR_MESSAGES["required"],
            "blank": ERROR_MESSAGES["blank"],
            "null": ERROR_MESSAGES["null"],
        },
    )

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__access_token_class = AccessToken

    def validate_access_token(self, value: str) -> AccessToken:
        """Check that the access token is valid and expired."""

        try:
            decode(
                jwt=value,
                key=SIMPLE_JWT["SIGNING_KEY"],
                algorithms=[SIMPLE_JWT["ALGORITHM"]],
            )
        except ExpiredSignatureError:
            access_token = self.__access_token_class(token=value, verify=False)

            try:
                access_token.check_blacklist()
            except TokenError as exc:
                raise JWTAPIError(detail=exc.args[0])

            return access_token
        except DecodeError:
            message = INVALID_OR_EXPIRED

            raise JWTAPIError(
                detail=message.format(token_type=AccessToken.token_type)
            )

        raise JWTAPIError(detail=ACCESS_NOT_EXPIRED)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the request data before continuing."""

        # Validate the data provided in the request body
        unknown_fields = set(self.initial_data) - set(self.fields)

        if unknown_fields:
            raise serializers.ValidationError(
                code="invalid_data",
                detail={
                    field: "This field is not allowed." for field in unknown_fields
                },
            )

        return attrs
