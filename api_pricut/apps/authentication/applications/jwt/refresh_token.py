from apps.authentication.jwt import AccessToken, JWTErrorMessages
from apps.authentication.domain.typing import JSONWebToken
from apps.users.domain.interfaces import IUserRepository
from apps.exceptions import JWTAPIError


# Error messages
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value


class UseCaseRefreshToken:
    """
    Use case responsible for updating the user access token.

    This class interacts with the user repository injected as a dependency to update
    the user access token.
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        self.__user_repository = user_repository
        self.__access_token_class = AccessToken

    def refresh_token(self, access_token: AccessToken) -> JSONWebToken:
        """
        Update the user access token.

        #### Parameters:
        - access_token: The access token to update.

        #### Raises:
        - `JWTAPIError`: If the access token user does not exist in the database.
        """

        user = self.__user_repository.get_user(
            filters={"uuid": access_token.payload["user_uuid"]}
        ).first()

        if user is None:
            raise JWTAPIError(detail=USER_NOT_FOUND)

        return self.__access_token_class(user=user, verify=False).token_encoded
