from apps.users.domain.entities import User
from django.db.models import Model, QuerySet
from typing import Dict, Tuple, Any
from abc import ABC, abstractmethod


class IUserRepository(ABC):
    """
    UserRepository interface.

    This interface defines the contract for a repository that manages
    `User` entity in the database. This class provides methods that
    perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def create_user(cls, data: Dict[str, Any], user_role: str) -> User:
        """
        Creates a user in the database with the provided data.

        #### Parameters:
        - data: The data to create the user with.
        - user_role: The role of the user to create.

        #### Raises:
        - DatabaseConnectionAPIError: If there is an operational error with the
        database.
        """

        pass

    @classmethod
    @abstractmethod
    def get_user(
        cls,
        filters: Dict[str, Any],
        get_role_data: str = None,
    ) -> QuerySet[User]:
        """
        Retrieves a user from the database based on the provided filters.

        #### Parameters:
        - filters: The filters to use to retrieve the user.
        - get_role_data: The role data to prefetch when retrieving the user.

        #### Raises:
        - DatabaseConnectionAPIError: If there is an operational error with the
        database.
        """

        pass

    @classmethod
    @abstractmethod
    def update_user(
        cls,
        base_user_instance: User = None,
        user_role_instance: Model = None,
        base_data: Dict[str, Any] = None,
        role_data: Dict[str, Any] = None,
    ) -> Tuple[User, Model]:
        """
        Updates a user's base information or role in the database with the data
        provided.

        #### Parameters:
        - base_user_instance: The user instance to update.
        - user_role_instance: The role instance to update.
        - base_data: The data to update the user's base information with.
        - role_data: The data to update the user's role with.

        #### Raises:
        - DatabaseConnectionAPIError: If there is an operational error with the
        database.
        """

        pass

    @classmethod
    @abstractmethod
    def exists(cls, model_name: str, data: Dict[str, Any]) -> bool:
        """
        Checks if a user with the provided data exists in the database.

        #### Parameters:
        - model_name: The name of the model to check if the user exists.
        - data: The data to use to check if the user exists.

        #### Raises:
        - ValueError: If the model name provided is invalid.
        - DatabaseConnectionAPIError: If there is an operational error with the
        database.
        """

        pass
