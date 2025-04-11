from apps.dashboard.infrastructure.serializers import (
    CutBaseInfoSerializer as Serializer,
)
from apps.dashboard.domain.constants import CutDataProperties
from apps.exceptions import (
    DatabaseConnectionAPIError,
    NotAuthenticatedAPIError,
    PermissionDeniedAPIError,
    JWTAPIError,
)
from apps.authentication.jwt import JWTErrorMessages
from apps.utils import ERROR_MESSAGES, StaticInfoErrorMessages
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    extend_schema_serializer,
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)


# Cutting techniques data properties
NAME_MAX_LENGTH = CutDataProperties.NAME_MAX_LENGTH.value


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value.format(token_type="access")
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value.format(
    token_type="access"
)


CutBaseInfoSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Thickness data",
            description=f"This is the data to create a new service. The following validations will be applied:\n- **Name:** This field is required, must not exceed {NAME_MAX_LENGTH} characters and cannot be in use.\n\nFields other than those defined for this request are not allowed.",
            value={"name": "Corte láser"},
            request_only=True,
        ),
    ],
)


@CutBaseInfoSerializerSchema
class CutBaseInfoSerializer(Serializer):
    pass


UpdateCutBaseInfo = extend_schema(
    operation_id="update_cut_base_info",
    tags=["Dashboard"],
    parameters=[
        OpenApiParameter(
            name="cut_code",
            description="The code of the cutting technique to be updated.",
            required=True,
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.STR,
        ),
    ],
    request=CutBaseInfoSerializer,
    responses={
        200: OpenApiResponse(
            description="**(OK)** The cutting technique has been updated successfully.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "name": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="cut_updated",
                    summary="Cutting technique updated",
                    description="The base information of the cutting technique has been updated successfully.",
                    value={
                        "code": "corte_laser",
                        "name": "Corte láser",
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
            description="**(UNAUTHORIZED)** The JWT is not valid to continue with the request or the request cannot be completed.",
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
                    description="This response is displayed when the user does not have permission to update the cutting technique.",
                    value={
                        "code": PermissionDeniedAPIError.default_code,
                        "detail": PermissionDeniedAPIError.default_detail,
                    },
                ),
            ],
        ),
        404: OpenApiResponse(
            description="**(NOT_FOUND)** Some resources necessary for this process were not found in the database.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="cut_not_found",
                    summary="Cutting technique not found",
                    description="The cutting technique was not found in the database.",
                    value={
                        "code": CUT_NOT_FOUND["code"],
                        "detail": CUT_NOT_FOUND["detail"],
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
