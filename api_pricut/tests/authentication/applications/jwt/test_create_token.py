from apps.authentication.applications import UseCaseCreateToken
from apps.authentication.domain.entities import JWT, JWTBlacklist
from apps.users.domain.constants import NATURAL_PERSON_ROLE, COMPANY_ROLE
from apps.exceptions import (
    DatabaseConnectionAPIError,
    PermissionDeniedAPIError,
    AuthenticationFailedAPIError,
)
from settings.environments.base import SIMPLE_JWT
from tests.factories import UserFactory
from unittest.mock import Mock, patch
from jwt import decode
import pytest


@pytest.mark.django_db
class TestUseCaseCreateToken:
    """
    This class encapsulates all the tests for the use case in charge of
    authenticating users with JSON Web Token.

    A successful login will generate an access token and an update token for the
    user, provided their account is active and they have permission to authenticate
    using JSON Web Token.
    """

    application_class = UseCaseCreateToken
    user_factory = UserFactory

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_authenticated_user(self, user_role: str, load_user_groups) -> None:
        """
        This test is responsible for validating the expected behavior of the use case
        when the request data is valid.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            add_perm=True,
            save=True,
        )
        data = user_factory_obj.data

        # Instantiating the application and calling the method
        access_token = self.application_class.validate_credentials(
            credentials={
                "email": data["base_data"]["email"],
                "password": data["base_data"]["password"],
            }
        )

        # Assert that the generated tokens were saved in the database
        access_payload = decode(
            jwt=access_token,
            key=SIMPLE_JWT["SIGNING_KEY"],
            algorithms=[SIMPLE_JWT["ALGORITHM"]],
        )
        access_token_obj = (
            JWT.objects.filter(jti=access_payload["jti"])
            .select_related("user")
            .first()
        )

        assert access_token_obj
        assert JWTBlacklist.objects.count() == 0

        # Asserting that the tokens were created with the correct data
        assert str(access_token_obj.user.uuid) == access_payload["user_uuid"]
        assert access_token_obj.jti == access_payload["jti"]
        assert access_token_obj.token == access_token
        assert access_payload["user_role"] == user_role

    def test_if_credentials_invalid(self) -> None:
        """
        This test is responsible for validating the expected behavior of the use case
        when the credentials provided are invalid.
        """

        # Instantiating the application and calling the method
        with pytest.raises(AuthenticationFailedAPIError):
            self.application_class.validate_credentials(
                credentials={
                    "email": "user1@email.com",
                    "password": "contraseña1234",
                }
            )

        # Asserting that the user does not exist in the database
        assert JWT.objects.count() == 0
        assert JWTBlacklist.objects.count() == 0

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_if_inactive_user_account(
        self,
        user_role: str,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the use case
        when the user account is inactive.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            add_perm=True,
            active=False,
            save=True,
        )
        data = user_factory_obj.data

        # Instantiating the application and calling the method
        with pytest.raises(AuthenticationFailedAPIError):
            self.application_class.validate_credentials(
                credentials={
                    "email": data["base_data"]["email"],
                    "password": data["base_data"]["password"],
                }
            )

        # Asserting that the user does not exist in the database
        assert JWT.objects.count() == 0
        assert JWTBlacklist.objects.count() == 0

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_if_user_has_not_permission(self, user_role: str) -> None:
        """
        This test is responsible for validating the expected behavior of the use case
        when the user does not have the necessary permissions to perform the action.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            save=True,
        )
        data = user_factory_obj.data

        # Instantiating the application and calling the method
        with pytest.raises(PermissionDeniedAPIError):
            _ = self.application_class.validate_credentials(
                credentials={
                    "email": data["base_data"]["email"],
                    "password": data["base_data"]["password"],
                }
            )

        # Asserting that the user does not exist in the database
        assert JWT.objects.count() == 0
        assert JWTBlacklist.objects.count() == 0

    @patch(
        target="apps.authentication.backends.EmailBackend.authenticate",
        side_effect=DatabaseConnectionAPIError,
    )
    def test_if_conection_db_failed(self, backend_mock: Mock) -> None:
        """
        Test that validates the expected behavior of the use case when the connection
        to the database fails.
        """

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            self.application_class.validate_credentials(
                credentials={
                    "email": "user1@email.com",
                    "password": "contraseña1234",
                }
            )

        # Asserting that the user does not exist in the database
        assert JWT.objects.count() == 0
        assert JWTBlacklist.objects.count() == 0
