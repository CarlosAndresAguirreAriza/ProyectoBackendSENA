from apps.dashboard.infrastructure.serializers import (
    CreateThicknessSerializer as Serializer,
)
from apps.dashboard.domain.constants import ThicknessDataProperties
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

# Thickness data properties
MAX_DIGITS = ThicknessDataProperties.MAX_DIGITS.value
DECIMAL_PLACES = ThicknessDataProperties.DECIMAL_PLACES.value
MAX_VALUE = ThicknessDataProperties.MAX_VALUE.value
MIN_VALUE = ThicknessDataProperties.MIN_VALUE.value

# Error messages
MATERIAL_NOT_FOUND = StaticInfoErrorMessages.MATERIAL_NOT_FOUND.value
NOT_ADD_THICKNESS = StaticInfoErrorMessages.NOT_ADD_THICKNESS.value
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value.format(token_type="access")
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value.format(
    token_type="access"
)


CreateThicknessSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Thickness data",
            description=f"These are the data of a material that can be updated, the following validations will be applied to each data:\n- **Value:** This field is required and must be a decimal number with a maximum of {MAX_DIGITS} digits before the comma, up to {DECIMAL_PLACES} decimal places, a minimum value of {float(MAX_VALUE)} and a maximum value of {float(MIN_VALUE)}.\n- **Compatibility cut:** This field is required, the cutting technique must exist in the database and at least one cutting technique must be defined as compatible with the thickness.\n\nFields other than those defined for this request are not allowed.",
            value={
                "value": 6.5,
                "compatibility_cut": {
                    "laser_fibra": True,
                    "laser_co2": False,
                    "router_cnc": False,
                },
            },
            request_only=True,
        ),
    ],
)


@CreateThicknessSerializerSchema
class CreateThicknessSerializer(Serializer):
    pass


CreateThicknessSchema = extend_schema(
    operation_id="add_thickness",
    tags=["Dashboard"],
    parameters=[
        OpenApiParameter(
            name="material_code",
            description="The code of the material to which the new thickness is to be added.",
            required=True,
            location=OpenApiParameter.PATH,
            type=OpenApiTypes.STR,
        ),
    ],
    request=CreateThicknessSerializer,
    responses={
        201: OpenApiResponse(
            description="**(OK)** Thickness was added successfully.",
            response={
                "properties": {
                    "modified_thicknesses": {"type": "boolean"},
                    "data": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "value": {"type": "decimal"},
                            "compatibility_cut": {
                                "type": "object",
                                "properties": {
                                    "cut_code": {"type": "boolean"},
                                },
                            },
                        },
                    },
                }
            },
            examples=[
                OpenApiExample(
                    name="add_thickness",
                    summary="Thickness added",
                    description="The thickness was added successfully. The **modified_thicknesses** field indicates whether the information for all materials cached in the browser needs to be updated.",
                    value={
                        "modified_thicknesses": False,
                        "data": {
                            "id": 1,
                            "value": 0.5,
                            "compatibility_cut": {
                                "laser_fibra": True,
                                "laser_co2": False,
                                "router_cnc": False,
                            },
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
                            "value": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_whole_digits"].format(
                                    max_whole_digits=MAX_DIGITS - DECIMAL_PLACES,
                                ),
                                ERROR_MESSAGES["max_digits"].format(
                                    max_digits=MAX_DIGITS,
                                ),
                                ERROR_MESSAGES["decimal_places"].format(
                                    decimal_places=DECIMAL_PLACES,
                                ),
                                ERROR_MESSAGES["max_value"].format(
                                    max_value=float(MAX_VALUE),
                                ),
                                ERROR_MESSAGES["min_value"].format(
                                    min_value=float(MIN_VALUE),
                                ),
                            ],
                            "compatibility_cut": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["empty"],
                                ERROR_MESSAGES["compatibility_cut"],
                                ERROR_MESSAGES["not_a_dict"].format(
                                    input_type="list",
                                ),
                                ERROR_MESSAGES["cut_not_exist"].format(
                                    cut_code="other_cut"
                                ),
                            ],
                        },
                    },
                ),
                OpenApiExample(
                    name="compatibility_cut_errors",
                    summary="Compatibility cut errors",
                    description="These are the possible error messages for the compatibility cut field.",
                    value={
                        "compatibility_cut": {
                            "cut_code": [
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                            ]
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
                    summary="STATIC INFO - Cutting technique inactive",
                    description="This response is returned when the cutting technique is inactive.",
                    value={
                        "code": NOT_ADD_THICKNESS["code"],
                        "detail": NOT_ADD_THICKNESS["detail"],
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
                    description="This response is displayed when the user does not have permission to add a new thickness to a material or does not have the required role.",
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
                    description="The material to which the thickness is to be added was not found in the database.",
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
