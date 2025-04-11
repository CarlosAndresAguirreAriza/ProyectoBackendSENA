from apps.users.infrastructure.repositories import UserRepository
from apps.users.applications import UseCaseRegisterUser
from apps.users.domain.constants import NATURAL_PERSON_ROLE
from apps.users.domain.entities import User, NaturalPersonRole
from apps.permissions import PERMISSIONS, USER_ROLE_PERMISSIONS
from apps.exceptions import DatabaseConnectionAPIError
from tests.factories import UserFactory
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestCreateNaturalPersonApplication:
    """
    This class encapsulates the tests for the use case or business logic
    responsible for creating a user with the "natural person" role.
    """

    application_class = UseCaseRegisterUser
    user_factory = UserFactory

    def test_created_successfully(self, load_user_groups) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a user is created successfully.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE
        )
        data = user_factory_obj.data
        base_data = data["base_data"]
        role_data = data["role_data"]
        base_data["confirm_password"] = base_data["password"]
        role_data.pop("phone_number")
        role_data.pop("address")
        role_data.pop("cc")

        # Instantiating the application and calling the method
        use_case = self.application_class(user_repository=UserRepository)
        use_case.create_natural_person(data={**base_data, **role_data})

        # Asserting that the user was created successfully
        base_user = User.objects.filter(email=base_data["email"]).first()
        role_user = NaturalPersonRole.objects.filter(
            first_name=role_data["first_name"]
        ).first()

        assert base_user is not None
        assert role_user is not None

        # Asserting that the user has the correct data
        assert base_user.email == base_data["email"]
        assert base_user.check_password(raw_password=base_data["password"])
        assert base_user.role == NATURAL_PERSON_ROLE
        assert base_user.is_active == True
        assert base_user.is_deleted == False
        assert role_user.first_name == role_data["first_name"]
        assert role_user.last_name == role_data["last_name"]
        assert role_user.address == None
        assert role_user.cc == None
        assert role_user.phone_number == None

        # Asserting that the user has the correct permissions
        perm_model_level = USER_ROLE_PERMISSIONS[NATURAL_PERSON_ROLE]

        for name in perm_model_level:
            assert base_user.has_perm(perm=PERMISSIONS[name])

    def test_if_conection_db_failed(self) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a DatabaseConnectionAPIError exception is raised.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE
        )
        data = user_factory_obj.data
        base_data = data["base_data"]
        role_data = data["role_data"]
        base_data["confirm_password"] = base_data["password"]
        role_data.pop("phone_number")
        role_data.pop("address")
        role_data.pop("cc")

        # Mocking the methods
        user_repository = Mock()
        create_user: Mock = user_repository.create_user
        create_user.side_effect = DatabaseConnectionAPIError

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(user_repository=user_repository)
            use_case.create_natural_person(data={**base_data, **role_data})
