from apps.users.domain.entities import User
from .entities import JWT
from .typing import JSONWebToken, JWTPayload
from django.db.models import QuerySet
from typing import Dict, Any
from abc import ABC, abstractmethod


class IJWTRepository(ABC):
    """
    JWTRepository interface.

    This interface defines the contract for a repository that manages
    `JWT` and `JWTBlacklist` entities in the database. This class provides
    methods that perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def get_token(cls, filters: Dict[str, Any]) -> QuerySet[JWT]:
        """
        Retrieve a access token from the database based on the provided filters.

        #### Parameters:
        - filters: The filters to use to retrieve the access token.

        #### Raises:
        - `DatabaseConnectionAPIError`: If there is an operational error with the
        database.
        """

        pass

    @classmethod
    @abstractmethod
    def add_checklist(
        cls,
        token: JSONWebToken,
        payload: JWTPayload,
        user: User,
    ) -> None:
        """
        Associate a access token with a user by adding it to the `checklist`.

        This way you can keep track of which tokens are associated with which
        users, and which tokens created are pending expiration or invalidation.

        #### Parameters:
        - token: The access token to associate with the user.
        - payload: The payload of the access token.
        - user: The user to associate the access token with.

        #### Raises:
        - `DatabaseConnectionAPIError`: If there is an operational error with the
        database.
        """

        pass

    @classmethod
    @abstractmethod
    def add_blacklist(cls, token: JWT) -> None:
        """
        Invalidates a access token by adding it to the `blacklist`.

        Once a token is blacklisted, it can no longer be used for authentication
        purposes until it is removed from the blacklist or has expired.

        #### Parameters:
        - token: The access token to invalidate.

        #### Raises:
        - `DatabaseConnectionAPIError`: If there is an operational error with the
        database.
        """

        pass

    @classmethod
    @abstractmethod
    def exists_blacklist(cls, jti: str) -> bool:
        """
        Check if a token exists in the blacklist.

        #### Parameters:
        - jti: The JSON Web Token Identifier to check if it exists in the blacklist.

        #### Raises:
        - `DatabaseConnectionAPIError`: If there is an operational error with the
        database.
        """

        pass
