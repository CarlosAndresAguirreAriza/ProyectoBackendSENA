from apps.authentication.infrastructure.serializers import (
    JWTLoginSerializer as Serializer,
)
from apps.authentication.domain.constants import ACCESS_TOKEN_LIFETIME
from apps.authentication.jwt import JWTErrorMessages
from apps.users.domain.constants import BaseUserDataProperties
from apps.exceptions import (
    AuthenticationFailedAPIError,
    DatabaseConnectionAPIError,
    PermissionDeniedAPIError,
)
from apps.utils import ERROR_MESSAGES
from rest_framework.fields import CharField
from drf_spectacular.utils import (
    extend_schema_serializer,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema
from typing import Dict


# This constant is used when the serializer error messages are the default.
DEFAULT_ERROR_MESSAGES = CharField().error_messages

# User base data properties
EMAIL_MAX_LENGTH = BaseUserDataProperties.EMAIL_MAX_LENGTH.value
PASSWORD_MAX_LENGTH = BaseUserDataProperties.PASSWORD_MAX_LENGTH.value


class JWTAuth(OpenApiAuthenticationExtension):
    """
    This class is used to add the JWT authentication schema to the OpenAPI
    documentation.
    """

    target_class = "apps.authentication.jwt.JWTAuthentication"
    name = "JWTAuth"
    match_subclasses = True

    def get_security_definition(self, auto_schema: AutoSchema) -> Dict[str, str]:
        """This method is used to return the JWT authentication schema."""

        return {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "To use endpoints that employ **JSON Web Token** as an authentication tool, you must enter the access token you obtained when using the endpoint (`POST api/v1/user/jwt/login/`).\n\n**Example:**\n\n<access_token>",
        }


JWTLoginSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Valid data for the request.",
            description=f"Valid credentials for a user. The following validations will be applied:\n- **Email:** This field is required and must not exceed {EMAIL_MAX_LENGTH} characters.\n- **Password:** This field is required and must not exceed {PASSWORD_MAX_LENGTH} characters.\n\nFields other than those defined for this request are not allowed.",
            value={
                "email": "user1@email.com",
                "password": "contraseña1234",
            },
            request_only=True,
        ),
    ],
)


@JWTLoginSerializerSchema
class JWTLoginSerializer(Serializer):
    pass


JWTLoginSchema = extend_schema(
    operation_id="jwt_login",
    tags=["Authentication"],
    request=JWTLoginSerializer,
    responses={
        200: OpenApiResponse(
            description="**(OK)** Authenticated user.",
            response={"properties": {"access_token": {"type": "string"}}},
            examples=[
                OpenApiExample(
                    name="response_ok",
                    summary="User authenticated",
                    description=f"The user has been successfully authenticated and the access token is returned, with a duration of **{int(ACCESS_TOKEN_LIFETIME.total_seconds() / 60)}** minutes used to access protected API resources.",
                    value={
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzExMDU0MzYyLCJpYXQiOjE3MTEwNDcxNjIsImp0aSI6IjY0MTE2YzgyYjhmMDQzOWJhNTJkZGZmMzgyNzQ2ZTIwIiwidXNlcl9pZCI6IjJhNmI0NTNiLWZhMmItNDMxOC05YzM1LWIwZTk2ZTg5NGI2MyJ9.gfhWpy5rYY6P3Xrg0usS6j1KhEvF1HqWMiU7AaFkp9A",
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="**(BAD_REQUEST)** The request data are invalid, error message(s) are returned for each field that did not pass the validations. Some messages are in Spanish because they will be used in the frontend and visible to the user.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "object"},
                }
            },
            examples=[
                OpenApiExample(
                    name="invalid_data",
                    summary="Invalid data",
                    description="These are the possible error messages for each field.",
                    value={
                        "code": "invalid_request_data",
                        "detail": {
                            "email": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=EMAIL_MAX_LENGTH,
                                ),
                            ],
                            "password": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=PASSWORD_MAX_LENGTH,
                                ),
                            ],
                        },
                    },
                ),
                OpenApiExample(
                    name="data_not_allowed",
                    summary="Data not allowed",
                    description="The request data contains an invalid field.",
                    value={
                        "code": "invalid_request_data",
                        "detail": {
                            "invalid_field": ["This field is not allowed."],
                        },
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="**(UNAUTHORIZED)** The user you are trying to authenticate is not authorized, this is due to some of the following reasons.\n- Invalid credentials.\n- The user's account has not been activated.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="authentication_failed",
                    summary="Credentials invalid",
                    description="This response is displayed when a user with the provided email is not found or the password is incorrect.",
                    value={
                        "code": AuthenticationFailedAPIError.default_code,
                        "detail": JWTErrorMessages.AUTHENTICATION_FAILED.value,
                    },
                ),
                OpenApiExample(
                    name="user_inactive",
                    summary="Inactive user account",
                    description="This response is displayed when the user trying to authenticate has an inactive account.",
                    value={
                        "code": AuthenticationFailedAPIError.default_code,
                        "detail": JWTErrorMessages.INACTIVE_ACCOUNT.value,
                    },
                ),
            ],
        ),
        403: OpenApiResponse(
            description="**(FORBIDDEN)** The user trying to authenticate does not have the permissions to do so with JSON Web Token.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="permission_denied",
                    summary="Permission denied",
                    description="This response appears when the user trying to authenticate does not have the permissions to do so with JSON Web Token.",
                    value={
                        "code": PermissionDeniedAPIError.default_code,
                        "detail": PermissionDeniedAPIError.default_detail,
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            description="**(INTERNAL_SERVER_ERROR)** An unexpected error occurred.",
            response={
                "properties": {
                    "detail": {"type": "string"},
                    "code": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="database_connection_error",
                    summary="Database connection error",
                    description="The connection to the database could not be established.",
                    value={
                        "code": DatabaseConnectionAPIError.default_code,
                        "detail": DatabaseConnectionAPIError.default_detail,
                    },
                ),
            ],
        ),
    },
)
