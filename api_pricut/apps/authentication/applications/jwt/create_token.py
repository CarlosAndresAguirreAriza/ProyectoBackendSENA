from apps.authentication.domain.typing import JSONWebToken
from apps.authentication.jwt import AccessToken, JWTErrorMessages
from apps.permissions import PERMISSIONS
from apps.exceptions import (
    AuthenticationFailedAPIError,
    PermissionDeniedAPIError,
)
from django.contrib.auth import authenticate
from typing import Dict


# Error messages
AUTHENTICATION_FAILED = JWTErrorMessages.AUTHENTICATION_FAILED.value
INACTIVE_ACCOUNT = JWTErrorMessages.INACTIVE_ACCOUNT.value


class UseCaseCreateToken:
    """
    Use case responsible for authenticating a user.

    This class interacts with the `authenticate` method from Django's authentication
    system to authenticate a user with the given credentials and return an access
    token.
    """

    __access_token_class = AccessToken

    @classmethod
    def validate_credentials(cls, credentials: Dict[str, str]) -> JSONWebToken:
        """
        Authenticate a user with the given credentials and return access token.

        #### Parameters:
        - credentials: The user credentials to authenticate.

        #### Raises:
        - `AuthenticationFailedAPIError`: If the user authentication fails.
        - `PermissionDeniedAPIError`: If the user does not have the required
        permissions.
        """

        user = authenticate(**credentials)

        if user is None:
            raise AuthenticationFailedAPIError(detail=AUTHENTICATION_FAILED)
        if user.is_active is False:
            raise AuthenticationFailedAPIError(detail=INACTIVE_ACCOUNT)
        if user.has_perm(perm=PERMISSIONS["jwt_auth"]) is False:
            raise PermissionDeniedAPIError()

        return cls.__access_token_class(user=user, verify=False).token_encoded
