from apps.authentication.jwt import JWTErrorMessages, AccessToken
from apps.users.domain.constants import ADMIN_ROLE, NATURAL_PERSON_ROLE
from apps.dashboard.domain.entities import CuttingTechnique
from apps.exceptions import (
    DatabaseConnectionAPIError,
    PermissionDeniedAPIError,
    NotAuthenticatedAPIError,
    JWTAPIError,
)
from apps.utils import ERROR_MESSAGES, standardize_and_replace
from tests.factories import UserFactory, JWTFactory
from tests.utils import format_serializer_errors
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from deepdiff import DeepDiff
from typing import Dict, List, Any
import pytest


# Error messages
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value


@pytest.mark.django_db
class TestCreateCutAPIView:
    """
    This class encapsulates the tests for the view responsible for creating the
    cutting technique in the database.
    """

    path_name = "get_create_cut"
    user_factory = UserFactory
    jwt_factory = JWTFactory

    @pytest.mark.parametrize(
        argnames="request_data",
        argvalues=[
            {
                "name": "Nombre del servicio",
                "about_text": "Descripción del servicio.",
                "common_uses_text": "Usos comunes del servicio.",
                "card_text": "Descripción de la tarjeta.",
                "main_text": "Texto principal del servicio.",
                "banner_image": "https://image.png",
                "main_image": "https://image.png",
                "card_image": "https://image.png",
                "about_image": "https://image.png",
                "uses_image": "https://image.png",
            },
        ],
        ids=["valid_data"],
    )
    def test_if_create_cut(
        self,
        request_data: Dict[str, Any],
        client: Client,
        load_static_info,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view responsible for creating the cutting techniques in the database.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=ADMIN_ROLE,
            add_perm=True,
            save=True,
        )
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
            save=True,
        )

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data=request_data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that the correct data
        cut = CuttingTechnique.objects.filter(name=request_data["name"]).first()
        base_info = response.data["base_info"]
        descriptions = response.data["descriptions"]
        images = response.data["images"]

        assert response.status_code == status.HTTP_201_CREATED
        assert cut.name == base_info["name"]
        assert cut.code == standardize_and_replace(text=base_info["name"])
        assert cut.about_text == descriptions["about_text"]
        assert cut.common_uses_text == descriptions["common_uses_text"]
        assert cut.main_text == descriptions["main_text"]
        assert cut.card_text == descriptions["card_text"]
        assert cut.banner_image == images["banner_image"]
        assert cut.main_image == images["main_image"]
        assert cut.about_image == images["about_image"]
        assert cut.uses_image == images["uses_image"]
        assert cut.card_image == images["card_image"]
        assert cut.is_active == False

    @pytest.mark.parametrize(
        argnames="request_data, messages_expected",
        argvalues=[
            (
                {},
                {
                    "name": [ERROR_MESSAGES["required"]],
                    "about_text": [ERROR_MESSAGES["required"]],
                    "common_uses_text": [ERROR_MESSAGES["required"]],
                    "main_text": [ERROR_MESSAGES["required"]],
                    "card_text": [ERROR_MESSAGES["required"]],
                    "banner_image": [ERROR_MESSAGES["required"]],
                    "main_image": [ERROR_MESSAGES["required"]],
                    "about_image": [ERROR_MESSAGES["required"]],
                    "uses_image": [ERROR_MESSAGES["required"]],
                    "card_image": [ERROR_MESSAGES["required"]],
                },
            ),
            (
                {
                    "name": "Nombre del servicio",
                    "about_text": "Descripción del servicio.",
                    "common_uses_text": "Usos comunes del servicio.",
                    "card_text": "Descripción de la tarjeta.",
                    "main_text": "Texto principal del servicio.",
                    "banner_image": "image.png",
                    "main_image": "image.png",
                    "about_image": "image.png",
                    "uses_image": "image.png",
                    "card_image": "image.png",
                },
                {
                    "banner_image": [ERROR_MESSAGES["invalid_url"]],
                    "main_image": [ERROR_MESSAGES["invalid_url"]],
                    "about_image": [ERROR_MESSAGES["invalid_url"]],
                    "uses_image": [ERROR_MESSAGES["invalid_url"]],
                    "card_image": [ERROR_MESSAGES["invalid_url"]],
                },
            ),
            (
                {
                    "name": "Nombre del servicio",
                    "about_text": "Descripción del servicio.",
                    "common_uses_text": "Usos comunes del servicio.",
                    "card_text": "Descripción de la tarjeta.",
                    "main_text": "Texto principal del servicio.",
                    "banner_image": "https://image.png",
                    "main_image": "https://image.png",
                    "about_image": "https://image.png",
                    "uses_image": "https://image.png",
                    "card_image": "https://image.png",
                    "invalid_field": "invalid_field",
                },
                {"invalid_field": [ERROR_MESSAGES["invalid_field"]]},
            ),
        ],
        ids=[
            "empty_data",
            "invalid_url",
            "invalid_field",
        ],
    )
    def test_if_request_data_invalid(
        self,
        request_data: Dict[str, Any],
        messages_expected: Dict[str, List[str]],
        client: Client,
        load_static_info,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is valid.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=ADMIN_ROLE,
            add_perm=True,
            save=True,
        )
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
            save=True,
        )

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data=request_data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
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

    def test_if_access_token_not_provided(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the access token was not added in the request header.
        """

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data={},
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = NotAuthenticatedAPIError.status_code
        code_expected = NotAuthenticatedAPIError.default_code
        message_expected = NotAuthenticatedAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == code_expected
        assert response.data["detail"] == message_expected

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
        self,
        access_token: str,
        message_expected: str,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request access token is invalid.
        """

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data={},
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
        This test is responsible for validating the expected behavior of the
        view when the request access token is blacklisted.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=ADMIN_ROLE,
            save=True,
        )
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
            add_blacklist=True,
            save=True,
        )

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data={},
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
        user_factory_obj = self.user_factory.create_user(user_role=ADMIN_ROLE)
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
        )

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data={},
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == JWTAPIError.status_code
        assert response.data["code"] == JWTAPIError.default_code
        assert response.data["detail"] == USER_NOT_FOUND

    @pytest.mark.parametrize(
        argnames="user_role, add_perm",
        argvalues=[(NATURAL_PERSON_ROLE, True), (ADMIN_ROLE, False)],
        ids=["is_not_admin", "can_not_permission"],
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
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
        )

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data={},
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
        user_factory_obj = self.user_factory.create_user(user_role=ADMIN_ROLE)
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
        )

        # Simulating the request
        path = reverse(viewname=self.path_name)
        response = client.post(
            path=path,
            data={},
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
