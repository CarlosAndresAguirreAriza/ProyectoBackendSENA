from apps.users.domain.constants import (
    NaturalPersonDataProperties,
    NATURAL_PERSON_ROLE,
    COMPANY_ROLE,
)
from apps.authentication.jwt import AccessToken, JWTErrorMessages
from apps.exceptions import (
    DatabaseConnectionAPIError,
    NotAuthenticatedAPIError,
    PermissionDeniedAPIError,
    JWTAPIError,
)
from tests.factories import UserFactory, JWTFactory
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from typing import Dict, Any
from uuid import uuid4
import pytest


# Error messages
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value


@pytest.mark.django_db
class TestRetrieveNaturalPersonAPIView:
    """
    This class encapsulates the tests for the view responsible for retrieving
    information about a user with the `natural person` role.
    """

    path_name = "get_natural_person"
    user_factory = UserFactory
    jwt_factory = JWTFactory

    def test_if_get_user_data(self, client: Client, load_user_groups) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the request data is valid.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE,
            add_perm=True,
            save=True,
        )
        user = user_factory_obj.user
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user,
            save=True,
        )

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(user.uuid)},
            ),
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_200_OK
        assert "base_data" in response.data
        assert "role_data" in response.data

        base_data_fields = set(NaturalPersonDataProperties.BASE_DATA.value)
        base_data_fields.remove("password")
        role_data_fields = set(NaturalPersonDataProperties.ROLE_DATA.value)

        assert (
            bool(
                base_data_fields.symmetric_difference(
                    set(response.data["base_data"])
                )
            )
            is False
        )
        assert (
            bool(
                role_data_fields.symmetric_difference(
                    set(response.data["role_data"])
                )
            )
            is False
        )

    def test_if_access_token_not_provided(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the access token is not provided.
        """

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(uuid4())},
            ),
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = NotAuthenticatedAPIError.status_code
        code_expected = NotAuthenticatedAPIError.default_code
        message_expected = NotAuthenticatedAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == code_expected
        assert response.data["detail"] == message_expected

    def test_if_access_token_user_is_not_owner(
        self,
        client: Client,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the request data is valid.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE,
            add_perm=True,
            save=True,
        )
        user = user_factory_obj.user
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user,
            save=True,
        )

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(uuid4())},
            ),
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = PermissionDeniedAPIError.status_code
        response_code_expected = PermissionDeniedAPIError.default_code
        response_data_expected = PermissionDeniedAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected

    @pytest.mark.parametrize(
        argnames="user_role, add_perm",
        argvalues=[(COMPANY_ROLE, True), (NATURAL_PERSON_ROLE, False)],
        ids=["is_not_role", "can_not_read_data"],
    )
    def test_if_user_has_not_permission(
        self,
        user_role: str,
        add_perm: bool,
        client: Client,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the user does not have the necessary role and permissions to perform
        the action.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            add_perm=add_perm,
            save=True,
        )
        user = user_factory_obj.user
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user,
        )

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(user.uuid)},
            ),
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = PermissionDeniedAPIError.status_code
        response_code_expected = PermissionDeniedAPIError.default_code
        response_data_expected = PermissionDeniedAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected

    @pytest.mark.parametrize(
        argnames="access_token, message_expected",
        argvalues=[
            (
                JWTFactory.create_token(
                    token_type=AccessToken.token_type,
                    invalid=True,
                ).token,
                INVALID_OR_EXPIRED.format(token_type=AccessToken.token_type),
            ),
            (
                JWTFactory.create_token(
                    token_type=AccessToken.token_type,
                    exp=True,
                ).token,
                INVALID_OR_EXPIRED.format(token_type=AccessToken.token_type),
            ),
        ],
        ids=[
            "access_token_invalid",
            "access_token_expired",
        ],
    )
    def test_if_token_validation_failed(
        self, access_token: Dict[str, Any], message_expected: str, client: Client
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the JWTs are invalid or expired.
        """

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(uuid4())},
            ),
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = JWTAPIError.status_code
        code_expected = JWTAPIError.default_code

        assert response.status_code == status_code_expected
        assert response.data["code"] == code_expected
        assert response.data["detail"] == message_expected

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
        user = user_factory_obj.user
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            add_blacklist=True,
            save=True,
            user=user,
        )

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(user.uuid)},
            ),
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = JWTAPIError.status_code
        code_expected = JWTAPIError.default_code
        message_expected = BLACKLISTED.format(token_type=AccessToken.token_type)

        assert response.status_code == status_code_expected
        assert response.data["code"] == code_expected
        assert response.data["detail"] == message_expected

    def test_if_user_not_found(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the view
        when the access token user is not found in the database.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE
        )
        user = user_factory_obj.user
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user,
        )

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(user.uuid)},
            ),
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == JWTAPIError.status_code
        assert response.data["code"] == JWTAPIError.default_code
        assert response.data["detail"] == USER_NOT_FOUND

    @patch(
        target="apps.authentication.jwt.JWTAuthentication.get_user",
        side_effect=DatabaseConnectionAPIError,
    )
    def test_if_conection_db_failed(
        self,
        jwt_class_mock: Mock,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when a DatabaseConnectionAPIError exception is raised.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=NATURAL_PERSON_ROLE
        )
        user = user_factory_obj.user
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user,
        )

        # Simulating the request
        response = client.get(
            path=reverse(
                viewname=self.path_name,
                kwargs={"user_uuid": str(user.uuid)},
            ),
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = DatabaseConnectionAPIError.status_code
        response_code_expected = DatabaseConnectionAPIError.default_code
        response_data_expected = DatabaseConnectionAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected
