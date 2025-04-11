from apps.authentication.jwt import JWTErrorMessages
from apps.exceptions import (
    DatabaseConnectionAPIError,
    NotAuthenticatedAPIError,
    PermissionDeniedAPIError,
    JWTAPIError,
)
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)


# Error messages
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value.format(token_type="access")
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value.format(
    token_type="access"
)


JWTLogoutSchema = extend_schema(
    operation_id="jwt_logout",
    tags=["Authentication"],
    request=None,
    responses={
        200: OpenApiResponse(description="**(OK)** Successfully closed session."),
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
                    description="This response is displayed when the user does not have permission to logout.",
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
