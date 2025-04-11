from apps.authentication.jwt import JWTErrorMessages, AccessToken
from apps.dashboard.domain.entities import ThicknessMaterial, UsesCuts
from apps.users.domain.constants import ADMIN_ROLE, NATURAL_PERSON_ROLE
from apps.exceptions import (
    DatabaseConnectionAPIError,
    PermissionDeniedAPIError,
    NotAuthenticatedAPIError,
    JWTAPIError,
)
from apps.utils import ERROR_MESSAGES
from tests.factories import UserFactory, JWTFactory
from tests.utils import format_serializer_errors
from rest_framework.fields import Field
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from typing import Dict, List, Any
import pytest


# Error messages
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value
DEFAULT_ERROR_MESSAGES = Field().error_messages


@pytest.mark.django_db
class TestAddThicknessAPIView:
    """
    This class encapsulates the tests for the view responsible for adding a new
    thickness to a material.
    """

    path_name = "create_thickness"
    user_factory = UserFactory
    jwt_factory = JWTFactory

    @pytest.mark.parametrize(
        argnames="material_code, data",
        argvalues=[
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                },
            ),
        ],
        ids=["material_mdf"],
    )
    def test_if_add_thickness(
        self,
        material_code: str,
        data: Dict[str, Any],
        client: Client,
        load_static_info,
        load_user_groups,
    ):
        """
        This test is responsible for validating the expected behavior of the
        view when a new thickness is added.
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
        path = reverse(
            viewname=self.path_name,
            kwargs={"material_code": material_code},
        )
        response = client.post(
            path=path,
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        argnames="material_code, data",
        argvalues=[
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                },
            ),
        ],
        ids=["material_mdf"],
    )
    def test_if_reactive_cut(
        self,
        material_code: str,
        data: Dict[str, Any],
        client: Client,
        load_static_info,
        load_user_groups,
    ):
        """
        This test is responsible for validating the expected behavior of the
        view when a cutting technique is reactivated.
        """

        # Prepare the appropriate scenario in the database
        cut_uses = UsesCuts.objects.get(cut__code="laser_fibra")
        cut_uses.number_uses = 0
        cut_uses.save()

        all_thicknesses = ThicknessMaterial.objects.all()

        for thickness in all_thicknesses:
            compatibility_cut = thickness.compatibility_cut
            compatibility_cut.pop("laser_fibra")
            thickness.compatibility_cut = compatibility_cut
            thickness.save()

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
        path = reverse(
            viewname=self.path_name,
            kwargs={"material_code": material_code},
        )
        response = client.post(
            path=path,
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        argnames="material_code, data, messages_expected",
        argvalues=[
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "other_cut": True,
                    },
                },
                {
                    "compatibility_cut": [
                        ERROR_MESSAGES["cut_not_exist"].format(
                            cut_code="other_cut"
                        ),
                    ]
                },
            ),
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": False,
                        "router_cnc": False,
                        "laser_co2": False,
                    },
                },
                {"compatibility_cut": [ERROR_MESSAGES["compatibility_cut"]]},
            ),
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                    "other_field": True,
                },
                {"other_field": [ERROR_MESSAGES["invalid_field"]]},
            ),
        ],
        ids=[
            "cut_not_exist",
            "cut_not_compatible",
            "invalid_field",
        ],
    )
    def test_if_invalid_data(
        self,
        material_code: str,
        data: Dict[str, Any],
        messages_expected: Dict[str, List[str]],
        client: Client,
        load_static_info,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is invalid.
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
        path = reverse(
            viewname=self.path_name,
            kwargs={"material_code": material_code},
        )
        response = client.post(
            path=path,
            data=data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "invalid_request_data"

        errors_formated = format_serializer_errors(data=response.data["detail"])

        for field, message in messages_expected.items():
            assert errors_formated[field] == message

    def test_if_access_token_not_provided(self, client: Client) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the access token was not added in the request header.
        """

        # Simulating the request
        path = reverse(viewname=self.path_name, kwargs={"material_code": "code"})
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
        self, access_token: str, message_expected: str, client: Client
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request access token is invalid.
        """

        # Simulating the request
        path = reverse(viewname=self.path_name, kwargs={"material_code": "code"})
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
        path = reverse(viewname=self.path_name, kwargs={"material_code": "code"})
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
        path = reverse(viewname=self.path_name, kwargs={"material_code": "code"})
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
        path = reverse(viewname=self.path_name, kwargs={"material_code": "code"})
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
        self, jwt_class_mock: Mock, client: Client
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
        path = reverse(viewname=self.path_name, kwargs={"material_code": "code"})
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
