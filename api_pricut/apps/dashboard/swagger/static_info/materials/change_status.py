from apps.dashboard.infrastructure.serializers import (
    StatusSerializer as Serializer,
)
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
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
    extend_schema,
)

# Error messages
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
STATUS_ERROR = StaticInfoErrorMessages.STATUS_ERROR.value
MATERIAL_NOT_FOUND = StaticInfoErrorMessages.MATERIAL_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value.format(token_type="access")
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value.format(
    token_type="access"
)


MaterialStatusSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Request data",
            description=f"These are the data required to change the status of a material:\n- **Status:** This field is required.\n\nFields other than those defined for this request are not allowed.",
            value={"status": False},
            request_only=True,
        ),
    ],
)


@MaterialStatusSerializerSchema
class MaterialStatusSerializer(Serializer):
    pass


MaterialStatusSchema = extend_schema(
    operation_id="change_material_status",
    tags=["Dashboard"],
    parameters=[
        OpenApiParameter(
            name="material_code",
            description="The code of the material to change the status.",
            required=True,
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.STR,
        ),
    ],
    request=MaterialStatusSerializer,
    responses={
        200: OpenApiResponse(
            description="**(OK)** The status of the material was updated successfully.",
            response={"properties": {"modified_thicknesses": {"type": "boolean"}}},
            examples=[
                OpenApiExample(
                    name="status_updated",
                    summary="Status updated",
                    description="The status of the material was updated successfully. The **modified_thicknesses** field indicates whether the information for all materials cached in the browser needs to be updated.",
                    value={"modified_thicknesses": True},
                ),
            ],
        ),
        400: OpenApiResponse(
            description="**(BAD_REQUEST)** The request data is invalid, error messages are returned for each field that failed validation. Some messages are in Spanish because they will be used in the frontend and visible to the user.",
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
                            "status": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
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
                OpenApiExample(
                    name="static_info_error_1",
                    summary="STATIC INFO - Invalid status value",
                    description="This response is returned when attempting to activate a material that is already active or deactivate a material that is already deactivated.",
                    value={
                        "code": STATUS_ERROR["code"],
                        "detail": STATUS_ERROR["detail"],
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
                    description="This response is displayed when the user does not have permission to change the status of a material.",
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
                    name="material_not_found",
                    summary="Material not found",
                    description="The material with the specified code was not found in the database.",
                    value={
                        "code": MATERIAL_NOT_FOUND["code"],
                        "detail": MATERIAL_NOT_FOUND["detail"],
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
