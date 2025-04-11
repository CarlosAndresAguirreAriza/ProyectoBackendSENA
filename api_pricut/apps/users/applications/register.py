from apps.users.domain.interfaces import IUserRepository
from apps.users.domain.constants import (
    NATURAL_PERSON_ROLE,
    COMPANY_ROLE,
    NaturalPersonDataProperties,
    CompanyDataProperties,
)
from typing import Dict, List, Any


class UseCaseRegisterUser:
    """
    Use cases responsible for registering users.

    This class interacts with repositories injected as dependencies to create
    new users in the database.
    """

    def __init__(self, user_repository: IUserRepository) -> None:
        self.__user_repository = user_repository

    def create_natural_person(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Create a new natural person user with the given data.

        #### Parameters:
        - data: The data to create the natural person user with.
        """

        data.pop("confirm_password")
        user_data = self.__reorganize_user_data(
            base_data_fields=NaturalPersonDataProperties.BASE_DATA.value,
            unorganized_data=data,
        )
        user_data["base_data"].setdefault("is_staff", False)
        user_data["base_data"].setdefault("is_superuser", False)
        user_data["base_data"].setdefault("is_active", True)
        user_data["base_data"].setdefault("is_deleted", False)
        self.__user_repository.create_user(
            user_role=NATURAL_PERSON_ROLE,
            data=user_data,
        )

    def create_company(self, data: Dict[str, Dict[str, Any]]) -> None:
        """
        Create a new company user with the given data.

        #### Parameters:
        - data: The data to create the company user with.
        """

        data.pop("confirm_password")
        user_data = self.__reorganize_user_data(
            base_data_fields=CompanyDataProperties.BASE_DATA.value,
            unorganized_data=data,
        )
        user_data["base_data"].setdefault("is_staff", False)
        user_data["base_data"].setdefault("is_superuser", False)
        user_data["base_data"].setdefault("is_active", True)
        user_data["base_data"].setdefault("is_deleted", False)
        self.__user_repository.create_user(
            user_role=COMPANY_ROLE,
            data=user_data,
        )

    @staticmethod
    def __reorganize_user_data(
        base_data_fields: List[str],
        unorganized_data: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Reorganize the data provided in the request body.

        #### Parameters:
        - base_data_fields: The fields that are considered base data for a user.
        - unorganized_data: The data to reorganize.
        """

        return {
            "base_data": {
                key: value
                for key, value in unorganized_data.items()
                if key in base_data_fields
            },
            "role_data": {
                key: value
                for key, value in unorganized_data.items()
                if key not in base_data_fields
            },
        }
