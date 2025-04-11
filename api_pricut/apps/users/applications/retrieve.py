from apps.users.domain.constants import NATURAL_PERSON_ROLE
from apps.users.domain.interfaces import IUserRepository
from apps.users.domain.entities import User
from apps.exceptions import ResourceNotFoundAPIError
from apps.utils import APIErrorMessages


# Error messages
USER_NOT_FOUND = APIErrorMessages.USER_NOT_FOUND.value


class UseCaseRetrieveUser:
    """
    Use case responsible for retrieving a user.

    This class interacts with repositories injected as dependencies to retrieve
    a user from the database.
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        self.__user_repository = user_repository

    def get_natural_person(self, user_uuid: str) -> User:
        """
        Retrieve a natural person user from the database.

        #### Parameters:
        - user_uuid: The UUID of the user to retrieve.

        #### Raises:
        - ResourceNotFoundAPIError: If the user is not found in the database.
        """

        user = self.__user_repository.get_user(
            get_role_data=NATURAL_PERSON_ROLE,
            filters={"uuid": user_uuid},
        ).first()

        if user is None:
            raise ResourceNotFoundAPIError(
                code=USER_NOT_FOUND["code"],
                detail=USER_NOT_FOUND["detail"],
            )

        return user
