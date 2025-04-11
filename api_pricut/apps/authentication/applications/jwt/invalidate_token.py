from apps.authentication.jwt import AccessToken


class UseCaseInvalidateToken:
    """Use case responsible for logging out a user."""

    @classmethod
    def invalidate_token(cls, access_token: AccessToken) -> None:
        """
        Logout a user by adding the access token to the blacklist.

        #### Parameters:
        - access_token: The access token to blacklist.
        """

        access_token.blacklist()
