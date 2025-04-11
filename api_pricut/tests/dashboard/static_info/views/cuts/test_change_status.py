from apps.authentication.jwt import JWTErrorMessages, AccessToken
from apps.users.domain.constants import ADMIN_ROLE, NATURAL_PERSON_ROLE
from apps.dashboard.domain.entities import CuttingTechnique
from apps.exceptions import (
    DatabaseConnectionAPIError,
    PermissionDeniedAPIError,
    NotAuthenticatedAPIError,
    ResourceNotFoundAPIError,
    StaticInfoAPIError,
    JWTAPIError,
)
from apps.utils import StaticInfoErrorMessages, ERROR_MESSAGES
from tests.factories import UserFactory, JWTFactory
from tests.utils import format_serializer_errors
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from typing import Dict, List
import pytest


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value
STATUS_ERROR = StaticInfoErrorMessages.STATUS_ERROR.value
INVALID_OR_EXPIRED = JWTErrorMessages.INVALID_OR_EXPIRED.value
BLACKLISTED = JWTErrorMessages.BLACKLISTED.value
USER_NOT_FOUND = JWTErrorMessages.USER_NOT_FOUND.value


@pytest.mark.django_db
class TestCutsChangeStatusAPIView:
    """
    This class encapsulates all tests for the view responsible for changing the
    status of the cutting technique.
    """

    path_name = "change_cut_status"
    user_factory = UserFactory
    jwt_factory = JWTFactory

    @pytest.mark.parametrize(
        argnames="cut_code, request_data",
        argvalues=[
            ("router_cnc", {"status": True}),
            ("laser_fibra", {"status": False}),
        ],
        ids=[
            "change_status_to_active",
            "change_status_to_inactive",
        ],
    )
    def test_if_change_cut_status(
        self,
        cut_code: str,
        request_data: Dict[str, bool],
        client: Client,
        load_static_info,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view responsible for changing the status of a cutting technique in
        the database.
        """

        # Prepare the appropriate scenario in the database
        cut_status = not request_data["status"]
        cut = CuttingTechnique.objects.filter(code=cut_code).first()
        cut.is_active = cut_status
        cut.save()

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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": cut_code})
        response = client.post(
            path=path,
            data=request_data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_200_OK
        assert response.data["modified_thicknesses"] == cut_status

    @pytest.mark.parametrize(
        argnames="cut_code, request_data",
        argvalues=[("other_cut", {"status": False})],
        ids=["cut_not_found"],
    )
    def test_if_not_found_cut(
        self,
        cut_code: str,
        request_data: Dict[str, bool],
        client: Client,
        load_static_info,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view responsible for changing the status of a cutting technique in
        the database when the cutting technique is not found.
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": cut_code})
        response = client.post(
            path=path,
            data=request_data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == ResourceNotFoundAPIError.status_code
        assert response.data["code"] == CUT_NOT_FOUND["code"]
        assert response.data["detail"] == CUT_NOT_FOUND["detail"]

    @pytest.mark.parametrize(
        argnames="cut_code, request_data",
        argvalues=[("laser_fibra", {"status": False})],
        ids=["router_cnc"],
    )
    def test_if_status_error(
        self,
        cut_code: str,
        request_data: Dict[str, bool],
        client: Client,
        load_static_info,
        load_user_groups,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view responsible for changing the status of a cutting technique in
        the database when the status is the same as the new status.
        """

        # Prepare the appropriate scenario in the database
        cut = CuttingTechnique.objects.filter(code=cut_code).first()
        cut.is_active = request_data["status"]
        cut.save()

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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": cut_code})
        response = client.post(
            path=path,
            data=request_data,
            HTTP_AUTHORIZATION=f"Bearer {jwt_factory_obj.token}",
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == StaticInfoAPIError.status_code
        assert response.data["code"] == STATUS_ERROR["code"]
        assert response.data["detail"] == STATUS_ERROR["detail"]

    @pytest.mark.parametrize(
        argnames="cut_code, request_data, messages_expected",
        argvalues=[
            (
                "mdf",
                {"status": True, "invalid_field": True},
                {"invalid_field": [ERROR_MESSAGES["invalid_field"]]},
            ),
        ],
        ids=["invalid_field"],
    )
    def test_if_request_data_invalid(
        self,
        cut_code: str,
        request_data: Dict[str, bool],
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": cut_code})
        response = client.post(
            path=path,
            data=request_data,
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": "cut_code"})
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": "cut_code"})
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": "cut_code"})
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": "cut_code"})
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": "cut_code"})
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
        path = reverse(viewname=self.path_name, kwargs={"cut_code": "cut_code"})
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
