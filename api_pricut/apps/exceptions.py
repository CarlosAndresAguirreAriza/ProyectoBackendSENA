from rest_framework.response import Response
from rest_framework.views import set_rollback
from rest_framework.exceptions import (
    APIException as BaseAPIException,
    NotFound,
)
from rest_framework import status
from django.http import Http404
from typing import Optional, Union, Dict, Any


def api_exception_handler(exc: Exception, context: Dict[str, Any]) -> Response:
    """
    Custom exception handler to return a response with a detailed error message.

    Args:
    - exc: The exception instance to be handled.
    - context: A dictionary containing the request object.
    """

    if isinstance(exc, Http404):
        exc = NotFound(*(exc.args))
    elif isinstance(exc, APIException):
        headers = {}

        if getattr(exc, "auth_header", None):
            headers["WWW-Authenticate"] = exc.auth_header
        elif getattr(exc, "wait", None):
            headers["Retry-After"] = "%d" % exc.wait

        data = {"detail": exc.detail}
        data["code"] = exc.code
        set_rollback()

        return Response(
            data,
            status=exc.status_code,
            headers=headers,
            content_type="application/json",
        )

    return None


class DetailDictMixin:
    """
    A mixin class that provides a method to build a detailed dictionary for the error.
    """

    default_detail: str
    default_code: str

    def __init__(
        self,
        detail: Union[Dict[str, Any], str, None] = None,
        code: Optional[str] = None,
    ) -> None:
        """
        Builds a detail dictionary for the error to give more information to API
        users.
        """

        detail_dict = {
            "detail": self.default_detail,
            "code": self.default_code,
        }

        if isinstance(detail, dict):
            detail_dict.update(detail)
        elif detail is not None:
            detail_dict["detail"] = detail
        elif code is not None:
            detail_dict["code"] = code

        super().__init__(detail_dict)


class APIException(BaseAPIException, DetailDictMixin):
    """
    Base class for exceptions raised in API views.
    """

    def __init__(
        self, detail: str | Dict[str, Any] = None, code: str = None
    ) -> None:
        """
        Initializes the exception during the execution of a API view with the given
        parameters.
        """

        self.detail = detail or self.default_detail
        self.code = code or self.default_code

        super().__init__(detail=self.detail, code=self.code)


# Authentication errors
class NotAuthenticatedAPIError(APIException):
    """Exception raised when the user is not authenticated."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Authentication credentials were not provided."
    default_code = "jwt_error"


class JWTAPIError(APIException):
    """Exception raised when a token error occurs."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Validation of the token failed."
    default_code = "jwt_error"


class AuthenticationFailedAPIError(APIException):
    """Exception raised when an authentication attempt fails."""

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Incorrect authentication credentials."
    default_code = "authentication_failed"


# API errors
class PermissionDeniedAPIError(APIException):
    """
    Exception raised when the user does not have permissions to perform an action.
    """

    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "The user does not have permissions to perform this action."
    default_code = "permission_denied"


class DatabaseConnectionAPIError(APIException):
    """
    Exception raised when a connection to the database cannot be established.
    """

    default_detail = "Service unavailable. Please try again later."
    default_code = "database_connection_error"


class ResourceNotFoundAPIError(APIException):
    """Exception raised when a requested resource is not found."""

    status_code = status.HTTP_404_NOT_FOUND
    default_detail = "requested resource not found."
    default_code = "resource_not_found"


class StaticInfoAPIError(APIException):
    """
    Exception that is generated when trying to perform an unauthorized operation on
    static information.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "This action is not permitted."
    default_code = "static_info_error"
