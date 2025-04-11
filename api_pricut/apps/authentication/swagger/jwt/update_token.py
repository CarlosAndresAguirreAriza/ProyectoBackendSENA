from apps.authentication.infrastructure.serializers import (
    JWTUpdateSerializer as Serializer,
)
from apps.authentication.jwt import JWTErrorMessages
from apps.exceptions import (
    DatabaseConnectionAPIError,
    JWTAPIError,
)
from rest_framework.fields import CharField
from drf_spectacular.utils import (
    extend_schema_serializer,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)


# Error messages
DEFAULT_ERROR_MESSAGES = CharField().error_messages
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value.format(token_type="access")
ACCESS_NOT_EXPIRED = (JWTErrorMessages.ACCESS_NOT_EXPIRED.value,)
TOKEN_NOT_FOUND = JWTErrorMessages.TOKEN_NOT_FOUND.value.format(
    token_type="access"
)
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value.format(
    token_type="access"
)


JWTUpdateSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Valid data for the request.",
            description=f"Valid data for the request. The following validations will be applied:\n- **Access token:** It is required, must be a valid token, must be expired and it should not exist on the blacklist.\n\nFields other than those defined for this request are not allowed.",
            value={
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1NjQ4MTAyLCJpYXQiOjE3MTU2NDA5MDIsImp0aSI6ImQ0YzEwYzEzMTgwODQ3YmNiNGU5NDMwMjFhYmQ3OGMyIiwidXNlcl91dWlkIjoiZDdiYTM0NzEtZWQzOS00NTQxLWFmOTktZWVmYzFjMWRlYmJkIiwicm9sZSI6IlNlYXJjaGVyVXNlciJ9.C5W1Q4XLBRXUbSUtKcESvudwo6-Ylg8u1fZZ4i79GWw",
            },
            request_only=True,
        ),
    ],
)


@JWTUpdateSerializerSchema
class JWTUpdateSerializer(Serializer):
    pass


JWTUpdateSchema = extend_schema(
    operation_id="jwt_update",
    tags=["Authentication"],
    request=JWTUpdateSerializer,
    responses={
        200: OpenApiResponse(
            description="**(OK)** New access token is generated.",
            response={
                "properties": {
                    "access_token": {"type": "string"},
                    "refresh_token": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="response_ok",
                    summary="New access token generated",
                    description="The new access token have been generated successfully, you can use these new token to keep the user authenticated.",
                    value={
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1NjQ4MTAyLCJpYXQiOjE3MTU2NDA5MDIsImp0aSI6ImQ0YzEwYzEzMTgwODQ3YmNiNGU5NDMwMjFhYmQ3OGMyIiwidXNlcl91dWlkIjoiZDdiYTM0NzEtZWQzOS00NTQxLWFmOTktZWVmYzFjMWRlYmJkIiwicm9sZSI6IlNlYXJjaGVyVXNlciJ9.C5W1Q4XLBRXUbSUtKcESvudwo6-Ylg8u1fZZ4i79GWw",
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="**(BAD_REQUEST)** The request data are invalid, error message(s) are returned for each field that did not pass the validations.",
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
                            "access_token": [
                                DEFAULT_ERROR_MESSAGES["required"],
                                DEFAULT_ERROR_MESSAGES["blank"],
                                DEFAULT_ERROR_MESSAGES["null"],
                                DEFAULT_ERROR_MESSAGES["invalid"],
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
            description="**(UNAUTHORIZED)** The JWT is not valid to continue with the request.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="user_not_found",
                    summary="JWT - User not found",
                    description="The user associated to the access token does not exist in the database.",
                    value={
                        "code": JWTAPIError.default_code,
                        "detail": USER_NOT_FOUND,
                    },
                ),
                OpenApiExample(
                    name="invalid_expired",
                    summary="JWT - Access token invalid or expired",
                    description="The access token is invalid or has expired.",
                    value={
                        "code": JWTAPIError.default_code,
                        "detail": INVALID_OR_EXPIRED,
                    },
                ),
                OpenApiExample(
                    name="token_blacklisted",
                    summary="JWT - Access token exists in the blacklist",
                    description="The access token exists in the blacklist.",
                    value={
                        "code": JWTAPIError.default_code,
                        "detail": BLACKLISTED,
                    },
                ),
                OpenApiExample(
                    name="token_not_found",
                    summary="JWT - Token not found",
                    description="The access token to be refreshed does not exist in the database.",
                    value={
                        "code": JWTAPIError.default_code,
                        "detail": TOKEN_NOT_FOUND,
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
