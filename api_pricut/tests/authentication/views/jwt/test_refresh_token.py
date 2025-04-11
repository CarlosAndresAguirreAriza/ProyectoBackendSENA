from apps.authentication.jwt import JWTErrorMessages, AccessToken
from apps.users.domain.constants import NATURAL_PERSON_ROLE, COMPANY_ROLE
from apps.exceptions import DatabaseConnectionAPIError, JWTAPIError
from apps.utils import ERROR_MESSAGES
from tests.factories import JWTFactory, UserFactory
from tests.utils import format_serializer_errors
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from deepdiff import DeepDiff
from typing import Dict
import pytest


# Error messages
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value
ACCESS_NOT_EXPIRED = JWTErrorMessages.ACCESS_NOT_EXPIRED.value


@pytest.mark.django_db
class TestRefreshTokenAPIView:
    """
    This class encapsulates all the tests of the view in charge of handling requests
    for the creation of new JWTs when the access token has expired.

    In order for the user to keep his session active, new JWTs can be generated using
    the refresh token, as long as the access token has expired.

    #### Clarifications:
    - The execution of this logic does not depend on the user's permissions; that is,
    the user's permissions are not validated.
    """

    path_name = "jwt_update"
    user_factory = UserFactory
    jwt_factory = JWTFactory

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_if_updated_token(self, user_role: str, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the request data is valid.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            save=True,
        )
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
            exp=True,
            save=True,
        )

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data={"access_token": jwt_factory_obj.token},
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.data

    def test_if_empty_request_data(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the request data is empty.
        """

        messages_expected = {
            "access_token": [ERROR_MESSAGES["required"]],
        }

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data={},
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

    @pytest.mark.parametrize(
        argnames="data, error_message",
        argvalues=[
            (
                {
                    "access_token": JWTFactory.create_token(
                        token_type=AccessToken.token_type,
                        invalid=True,
                    ).token
                },
                INVALID_OR_EXPIRED.format(token_type=AccessToken.token_type),
            ),
            (
                {
                    "access_token": JWTFactory.create_token(
                        token_type=AccessToken.token_type
                    ).token
                },
                ACCESS_NOT_EXPIRED,
            ),
        ],
        ids=[
            "access_token_invalid",
            "access_token_not_expired",
        ],
    )
    def test_if_token_validation_failed(
        self,
        data: Dict[str, str],
        error_message: str,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the JWTs are invalid or expired.
        """

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == JWTAPIError.status_code
        assert response.data["code"] == JWTAPIError.default_code
        assert response.data["detail"] == error_message

    def test_if_token_blacklisted(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the JWTs are blacklisted.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE,
            save=True,
        )
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
            add_blacklist=True,
            exp=True,
            save=True,
        )

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data={"access_token": jwt_factory_obj.token},
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == JWTAPIError.status_code
        assert response.data["code"] == JWTAPIError.default_code
        assert response.data["detail"] == BLACKLISTED.format(token_type="access")

    @patch(
        target="apps.authentication.applications.UseCaseRefreshToken.refresh_token",
        side_effect=JWTAPIError(detail=USER_NOT_FOUND),
    )
    def test_if_user_not_found(
        self,
        create_method_mock: Mock,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the user is not found in the database.
        """

        # Creating the JWTs to be used in the test
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            exp=True,
        )

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data={"access_token": jwt_factory_obj.token},
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == JWTAPIError.status_code
        assert response.data["code"] == JWTAPIError.default_code
        assert response.data["detail"] == USER_NOT_FOUND

    @patch(
        target="apps.authentication.applications.UseCaseRefreshToken.refresh_token",
        side_effect=DatabaseConnectionAPIError,
    )
    def test_if_conection_db_failed(
        self,
        new_tokens_mock: Mock,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when a DatabaseConnectionAPIError exception is raised.
        """

        # Creating the JWTs to be used in the test
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            exp=True,
        )

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data={"access_token": jwt_factory_obj.token},
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = DatabaseConnectionAPIError.status_code
        response_code_expected = DatabaseConnectionAPIError.default_code
        response_data_expected = DatabaseConnectionAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected
