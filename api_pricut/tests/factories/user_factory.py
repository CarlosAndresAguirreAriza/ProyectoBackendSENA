from apps.users.domain.entities import User
from apps.users.domain import constants
from tests.utils import fake
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from typing import Dict, List, Any
from copy import deepcopy


class UserFactory:
    """
    Factory class for creating users with fake data for testing purposes.

    This class provides methods to generate users with different roles, assign
    permissions, and manage their lifecycle in the database. It supports creating
    users with customizable attributes and roles, and optionally saving them to the
    database.

    #### Attributes:
    - user: the instance of the user created.
    - data: the data used to create the user object.
    """

    __model = User
    user: User = None
    data: Dict[str, Dict[str, Any]] = None

    @classmethod
    def create_user(
        cls,
        user_role: str,
        data: Dict[str, Dict[str, Any]] = {},
        active: bool = True,
        add_perm: bool = False,
        save: bool = False,
    ) -> "UserFactory":
        """
        Creates a user with the provided fake data. This data is used for testing
        purposes that require the existence of a user.

        #### Parameters:
        - user_role: the role of the user to be created.
        - data: the data to be used for the creation of the user.
        - active: whether the user is active or not.
        - add_perm: whether to add permissions to the user.
        - save: whether to save the user to the database.
        """

        # fmt: off
        user_data = {
            constants.NATURAL_PERSON_ROLE: cls.__natural_person_data(data_to_use=data),
            constants.COMPANY_ROLE: cls.__company_data(data_to_use=data),
            constants.ADMIN_ROLE: cls.__admin_data(data_to_use=data),
        }
        # fmt: on
        cls.data = user_data[user_role]
        cls.user = cls.__create(
            user_role=user_role,
            add_perm=add_perm,
            active=active,
            data=deepcopy(cls.data),
            save=save,
        )

        cls.data["base_data"].pop("is_staff")
        cls.data["base_data"].pop("is_superuser")
        cls.data["base_data"].pop("is_deleted")

        return cls

    @classmethod
    def __create(
        cls,
        data: Dict[str, Dict[str, Any]],
        user_role: str,
        active: bool,
        add_perm: bool,
        save: bool,
    ) -> User:
        """
        Creates a user with the provided data.

        #### Parameters:
        - user_role: the role of the user to be created.
        - data: the data to be used for the creation of the user.
        - active: whether the user is active or not.
        - add_perm: whether to add permissions to the user.
        - save: whether to save the user to the database.
        """

        email = data["base_data"].pop("email")
        password = data["base_data"].pop("password")
        user = cls.__model(
            **data["base_data"],
            role=user_role,
            is_active=active,
            email=email,
        )
        user.set_password(raw_password=password)
        related_model = ContentType.objects.get(model=user_role).model_class()
        role_data = related_model(base_data=user, **data["role_data"])

        if save is True:
            user.save()
            role_data.save()

            if add_perm is True:
                cls.__assign_permissions(user=user)

        return user

    @classmethod
    def __assign_permissions(cls, user: User) -> None:
        """This method assigns the permissions of the provided role to the user."""

        group = Group.objects.get(name=user.role)
        user.groups.add(group)
        user.save()

    @classmethod
    def __natural_person_data(
        cls,
        data_to_use: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        This method returns fake data for creating a user with the `narutal person` role.

        #### Parameters:
        - data_to_use: the data to be used for the creation of the user.
        """

        data_to_use = cls.__reorganize_user_data(
            base_data_fields=constants.NaturalPersonDataProperties.BASE_DATA.value,
            unorganized_data=data_to_use,
        )
        base_data_to_use = data_to_use.get("base_data")
        role_data_to_use = data_to_use.get("role_data")

        data = {
            "base_data": {
                "email": fake.email(),
                "password": fake.password(
                    length=11,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                ),
            },
            "role_data": {
                "phone_number": f"+59399111{fake.random_number(digits=4, fix_len=True)}",
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "address": fake.street_address(),
                "cc": fake.random_number(digits=10, fix_len=True),
            },
        }

        data["base_data"].setdefault("is_staff", False)
        data["base_data"].setdefault("is_superuser", False)
        data["base_data"].setdefault("is_deleted", False)

        if bool(base_data_to_use) is True:
            for key, value in base_data_to_use.items():
                data["base_data"].update({key: value})
        if bool(role_data_to_use) is True:
            for key, value in role_data_to_use.items():
                data["role_data"].update({key: value})

        return data

    @classmethod
    def __admin_data(
        cls,
        data_to_use: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        This method returns fake data for creating a user with the `admin` role.

        #### Parameters:
        - data_to_use: the data to be used for the creation of the user.
        """

        data_to_use = cls.__reorganize_user_data(
            base_data_fields=constants.NaturalPersonDataProperties.BASE_DATA.value,
            unorganized_data=data_to_use,
        )
        base_data_to_use = data_to_use.get("base_data")
        role_data_to_use = data_to_use.get("role_data")

        data = {
            "base_data": {
                "email": fake.email(),
                "password": fake.password(
                    length=11,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                ),
            },
            "role_data": {
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
            },
        }

        data["base_data"].setdefault("is_staff", True)
        data["base_data"].setdefault("is_superuser", False)
        data["base_data"].setdefault("is_deleted", False)

        if bool(base_data_to_use) is True:
            for key, value in base_data_to_use.items():
                data["base_data"].update({key: value})
        if bool(role_data_to_use) is True:
            for key, value in role_data_to_use.items():
                data["role_data"].update({key: value})

        return data

    @classmethod
    def __company_data(
        cls,
        data_to_use: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        This method returns fake data for creating a user with the `company` role.

        #### Parameters:
        - data_to_use: the data to be used for the creation of the user.
        """

        data_to_use = cls.__reorganize_user_data(
            base_data_fields=constants.NaturalPersonDataProperties.BASE_DATA.value,
            unorganized_data=data_to_use,
        )
        base_data_to_use = data_to_use.get("base_data")
        role_data_to_use = data_to_use.get("role_data")

        data = {
            "base_data": {
                "email": fake.email(),
                "password": fake.password(
                    length=11,
                    special_chars=True,
                    digits=True,
                    upper_case=True,
                    lower_case=True,
                ),
            },
            "role_data": {
                "name": fake.company(),
                "ruc": str(fake.random_number(digits=13, fix_len=True)),
                "phone_number": f"+59399111{fake.random_number(digits=4, fix_len=True)}",
                "address": fake.street_address(),
            },
        }

        data["base_data"].setdefault("is_staff", False)
        data["base_data"].setdefault("is_superuser", False)
        data["base_data"].setdefault("is_deleted", False)

        if bool(base_data_to_use) is True:
            for key, value in base_data_to_use.items():
                data["base_data"].update({key: value})
        if bool(role_data_to_use) is True:
            for key, value in role_data_to_use.items():
                data["role_data"].update({key: value})

        return data

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
