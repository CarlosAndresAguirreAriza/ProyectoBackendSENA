from apps.dashboard.infrastructure.serializers import (
    CutSerializer as Serializer,
)
from apps.dashboard.domain.constants import CutDataProperties
from apps.exceptions import (
    DatabaseConnectionAPIError,
    NotAuthenticatedAPIError,
    PermissionDeniedAPIError,
    JWTAPIError,
)
from apps.authentication.jwt import JWTErrorMessages
from apps.utils import ERROR_MESSAGES
from drf_spectacular.utils import (
    extend_schema_serializer,
    OpenApiResponse,
    OpenApiExample,
    extend_schema,
)


# Cutting techniques data properties
NAME_MAX_LENGTH = CutDataProperties.NAME_MAX_LENGTH.value
ABOUT_MAX_LENGTH = CutDataProperties.ABOUT_MAX_LENGTH.value
CARD_TEXT_MAX_LENGTH = CutDataProperties.CARD_TEXT_MAX_LENGTH.value
URL_MAX_LENGTH = CutDataProperties.URL_MAX_LENGTH.value
MAIN_TEXT_MAX_LENGTH = CutDataProperties.MAIN_TEXT_MAX_LENGTH.value
COMMON_USES_MAX_LENGTH = CutDataProperties.COMMON_USES_MAX_LENGTH.value

# Error messages
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value.format(token_type="access")
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value.format(
    token_type="access"
)


CutSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Cutting technique data",
            description=f"This is the data to create a new service. The following validations will be applied:\n- **Name:** This field is required, must not exceed {NAME_MAX_LENGTH} characters and cannot be in use.\n- **About text:** This field is required and must not exceed {ABOUT_MAX_LENGTH} characters.\n- **Card text:** This field is required and must not exceed {CARD_TEXT_MAX_LENGTH} characters.\n- **Common uses text:** This field is required and must not exceed {COMMON_USES_MAX_LENGTH} characters.\n- **Main text:** This field is required and must not exceed {MAIN_TEXT_MAX_LENGTH} characters.\n- **Images:** must follow the format of a valid URL of maximum {URL_MAX_LENGTH} characters.\n\nFields other than those defined for this request are not allowed.",
            value={
                "name": "Nombre del servicio",
                "about_text": "Descripción del servicio.",
                "card_text": "Descripción de la tarjeta servicio.",
                "common_uses_text": "Usos comunes del servicio.",
                "main_text": "Texto principal del servicio.",
                "banner_image": "https://image.png",
                "card_image": "https://image.png",
                "main_image": "https://image.png",
                "about_image": "https://image.png",
                "uses_image": "https://image.png",
            },
            request_only=True,
        ),
    ],
)


@CutSerializerSchema
class CutSerializer(Serializer):
    pass


CreateCutSchema = extend_schema(
    operation_id="create_cut",
    tags=["Dashboard"],
    request=CutSerializer,
    responses={
        201: OpenApiResponse(
            description="**(CREATED)** Cutting technique created successfully.",
            response={
                "properties": {
                    "base_info": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "code": {"type": "string"},
                        },
                    },
                    "descriptions": {
                        "type": "object",
                        "properties": {
                            "main_text": {"type": "string"},
                            "card_text": {"type": "string"},
                            "about_text": {"type": "string"},
                            "common_uses_text": {"type": "string"},
                        },
                    },
                    "images": {
                        "type": "object",
                        "properties": {
                            "banner_image": {"type": "string", "format": "uri"},
                            "card_image": {"type": "string", "format": "uri"},
                            "main_image": {"type": "string", "format": "uri"},
                            "about_image": {"type": "string", "format": "uri"},
                            "uses_image": {"type": "string", "format": "uri"},
                        },
                    },
                },
            },
            examples=[
                OpenApiExample(
                    name="cut_created",
                    summary="Cutting technique created",
                    description="The cutting technique was created successfully.",
                    value={
                        "base_info": {
                            "name": "Router CNC",
                            "code": "router_cnc",
                        },
                        "descriptions": {
                            "about_text": "Descripción de la técnica de corte.",
                            "common_uses_text": "Descripción de la tarjeta servicio.",
                            "main_text": "Acerca de la técnica de corte.",
                            "card_text": "Usos comunes de la técnica de corte.",
                        },
                        "images": {
                            "banner_image": "https://image.png",
                            "main_image": "https://image.png",
                            "card_image": "https://image.png",
                            "about_image": "https://image.png",
                            "uses_image": "https://image.png",
                        },
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="**(BAD_REQUEST)** The request data is invalid; error messages are returned for each field that failed validation. Some messages are in Spanish because they will be used in the frontend and visible to the user.",
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
                            "name": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["cut_exists"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=NAME_MAX_LENGTH,
                                ),
                            ],
                            "about_text": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=ABOUT_MAX_LENGTH,
                                ),
                            ],
                            "card_text": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=CARD_TEXT_MAX_LENGTH,
                                ),
                            ],
                            "common_uses_text": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=COMMON_USES_MAX_LENGTH,
                                ),
                            ],
                            "main_text": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=MAIN_TEXT_MAX_LENGTH,
                                ),
                            ],
                            "banner_image": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid_url"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=URL_MAX_LENGTH,
                                ),
                            ],
                            "card_image": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid_url"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=URL_MAX_LENGTH,
                                ),
                            ],
                            "main_image": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid_url"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=URL_MAX_LENGTH,
                                ),
                            ],
                            "about_image": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid_url"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=URL_MAX_LENGTH,
                                ),
                            ],
                            "uses_image": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid_url"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=URL_MAX_LENGTH,
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
                    name="access_token_not_provided",
                    summary="JWT - Access token not provided",
                    description="The access token was not provided in the request header.",
                    value={
                        "code": NotAuthenticatedAPIError.default_code,
                        "detail": NotAuthenticatedAPIError.default_detail,
                    },
                ),
            ],
        ),
        403: OpenApiResponse(
            description="**(FORBIDDEN)** The user does not have permission to access this resource.",
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
                    description="This response is displayed when the user does not have permission to create a cutting technique.",
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
