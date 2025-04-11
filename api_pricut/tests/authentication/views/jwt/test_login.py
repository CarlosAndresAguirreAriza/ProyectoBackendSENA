from apps.authentication.jwt import JWTErrorMessages
from apps.users.domain.constants import (
    BaseUserDataProperties,
    NATURAL_PERSON_ROLE,
    COMPANY_ROLE,
)
from apps.exceptions import (
    DatabaseConnectionAPIError,
    PermissionDeniedAPIError,
    AuthenticationFailedAPIError,
)
from apps.utils import ERROR_MESSAGES
from tests.utils import fake, format_serializer_errors
from tests.factories import UserFactory
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from deepdiff import DeepDiff
from typing import Dict, List
import pytest


# Base user data properties
EMAIL_MAX_LENGTH = BaseUserDataProperties.EMAIL_MAX_LENGTH.value
PASSWORD_MAX_LENGTH = BaseUserDataProperties.PASSWORD_MAX_LENGTH.value

# Error messages
AUTHENTICATION_FAILED = JWTErrorMessages.AUTHENTICATION_FAILED.value
INACTIVE_ACCOUNT = JWTErrorMessages.INACTIVE_ACCOUNT.value


@pytest.mark.django_db
class TestAuthenticationAPIView:
    """
    This class encapsulates all the tests of the view in charge of handling
    authentication requests for users with JSON Web Token.

    A successful login will generate an access token and an update token for the
    user, provided their account is active and they have permission to authenticate
    using JSON Web Token.
    """

    path_name = "jwt_login"
    user_factory = UserFactory

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_if_authentication_user(
        self,
        user_role: str,
        client: Client,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        responsible for authenticating users with JSON Web Token.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            add_perm=True,
            save=True,
        )
        data = user_factory_obj.data

        # Simulating the request
        credentials = {
            "email": data["base_data"]["email"],
            "password": data["base_data"]["password"],
        }
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=credentials,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

    @pytest.mark.parametrize(
        argnames="credentials, messages_expected",
        argvalues=[
            (
                {},
                {
                    "email": [ERROR_MESSAGES["required"]],
                    "password": [ERROR_MESSAGES["required"]],
                },
            ),
            (
                {
                    "email": f"{fake.bothify(text='?' * EMAIL_MAX_LENGTH)}@email.com",
                    "password": fake.password(
                        length=PASSWORD_MAX_LENGTH + 1,
                        special_chars=True,
                        digits=True,
                        upper_case=True,
                        lower_case=True,
                    ),
                },
                {
                    "email": [
                        ERROR_MESSAGES["max_length"].format(
                            max_length=EMAIL_MAX_LENGTH
                        ),
                    ],
                    "password": [
                        ERROR_MESSAGES["max_length"].format(
                            max_length=PASSWORD_MAX_LENGTH
                        ),
                    ],
                },
            ),
        ],
        ids=["missing_fields", "max_length_data"],
    )
    def test_if_request_data_invalid(
        self,
        credentials: Dict[str, str],
        messages_expected: Dict[str, List],
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is valid.
        """

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=credentials,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "invalid_request_data"

        # Asserting that the error messages are correct
        errors_formated = format_serializer_errors(data=response.data["detail"])

        for field, message in messages_expected.items():
            if isinstance(message, dict):
                diff = DeepDiff(
                    t1=errors_formated[field],
                    t2=message,
                    ignore_order=True,
                )
                assert not bool(diff)
            else:
                assert errors_formated[field] == message

    def test_if_credentials_invalid(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the credentials provided are invalid.
        """

        # Simulating the request
        credentials = {"email": "user1@emial.com", "password": "contraseña1234"}
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=credentials,
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = AuthenticationFailedAPIError.status_code
        response_code_expected = AuthenticationFailedAPIError.default_code

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == AUTHENTICATION_FAILED

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_if_inactive_user_account(
        self,
        user_role: str,
        client: Client,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
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

        # Simulating the request
        credentials = {
            "email": data["base_data"]["email"],
            "password": data["base_data"]["password"],
        }
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=credentials,
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = AuthenticationFailedAPIError.status_code
        response_code_expected = AuthenticationFailedAPIError.default_code

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == INACTIVE_ACCOUNT

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_if_user_has_not_permission(
        self,
        user_role: str,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the user does not have the necessary permissions to perform the action.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            save=True,
        )
        data = user_factory_obj.data

        # Simulating the request
        credentials = {
            "email": data["base_data"]["email"],
            "password": data["base_data"]["password"],
        }
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=credentials,
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = PermissionDeniedAPIError.status_code
        response_code_expected = PermissionDeniedAPIError.default_code
        response_data_expected = PermissionDeniedAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected

    @patch(
        target="apps.authentication.backends.EmailBackend.authenticate",
        side_effect=DatabaseConnectionAPIError,
    )
    def test_if_conection_db_failed(
        self,
        backend_mock: Mock,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when a DatabaseConnectionAPIError exception is raised.
        """

        # Simulating the request
        credentials = {"email": "user1@emial.com", "password": "contraseña1234"}
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=credentials,
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = DatabaseConnectionAPIError.status_code
        response_code_expected = DatabaseConnectionAPIError.default_code
        response_data_expected = DatabaseConnectionAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected
