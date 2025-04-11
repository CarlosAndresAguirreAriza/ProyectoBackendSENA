from apps.users.domain.constants import COMPANY_ROLE
from apps.exceptions import DatabaseConnectionAPIError
from apps.utils import ERROR_MESSAGES
from tests.utils import format_serializer_errors
from tests.factories import UserFactory
from rest_framework.fields import Field
from rest_framework import status
from django.test import Client
from django.urls import reverse
from unittest.mock import Mock, patch
from deepdiff import DeepDiff
from typing import Dict, Any
import pytest


DEFAULT_ERROR_MESSAGES = Field().error_messages


@pytest.mark.django_db
class TestCreateCompanyAPIView:
    """
    This class encapsulates the tests for the view responsible for creating a
    user with the `company` role.
    """

    path_name = "create_company"
    user_factory = UserFactory

    def test_if_created_user(self, client: Client, load_user_groups) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when a user is created successfully.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(user_role=COMPANY_ROLE)
        data = user_factory_obj.data
        base_data = data["base_data"]
        role_data = data["role_data"]
        base_data["confirm_password"] = base_data["password"]
        request_data = {**base_data, **role_data}

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=request_data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_201_CREATED

    @pytest.mark.parametrize(
        argnames="request_data, messages_expected",
        argvalues=[
            (
                {},
                {
                    "email": [ERROR_MESSAGES["required"]],
                    "password": [ERROR_MESSAGES["required"]],
                    "confirm_password": [ERROR_MESSAGES["required"]],
                    "name": [ERROR_MESSAGES["required"]],
                    "ruc": [ERROR_MESSAGES["required"]],
                    "phone_number": [ERROR_MESSAGES["required"]],
                    "address": [ERROR_MESSAGES["required"]],
                },
            ),
            (
                {
                    "email": "user1@email.com",
                    "password": "contraseñaUser1234",
                    "confirm_password": "contraseñaUser5678",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"confirm_password": [ERROR_MESSAGES["password_mismatch"]]},
            ),
            (
                {
                    "email": "user1@email.com",
                    "password": "contraseñaUser1234",
                    "confirm_password": "contraseñaUser5678",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                    "invalid_field": "Invalid field",
                },
                {"invalid_field": [ERROR_MESSAGES["invalid_field"]]},
            ),
        ],
        ids=[
            "empty_fields",
            "passwords_not_match",
            "invalid_field",
        ],
    )
    def test_if_request_data_invalid(
        self,
        request_data: Dict[str, Dict[str, Any]],
        messages_expected: Dict[str, Any],
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is invalid and does not exist in the database.
        """

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=request_data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "invalid_request_data"

        # Asserting that the error messages are correct
        errors_formated = format_serializer_errors(data=response.data["detail"])

        for field, messages in messages_expected.items():
            if isinstance(messages, dict):
                diff = DeepDiff(
                    t1=errors_formated[field],
                    t2=messages,
                    ignore_order=True,
                )
                assert not bool(diff)
            else:
                obtained = {*errors_formated[field]}
                expected = {*messages}

                assert bool(obtained.symmetric_difference(expected)) is False

    @pytest.mark.parametrize(
        argnames="request_data, messages_expected",
        argvalues=[
            (
                {
                    "email": "user1email.com",
                    "password": "contraseñaUser123",
                    "confirm_password": "contraseñaUser123",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"email": [ERROR_MESSAGES["invalid"]]},
            ),
            (
                {
                    "email": "user1@emailcom",
                    "password": "contraseña1234",
                    "confirm_password": "contraseña123",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"email": [ERROR_MESSAGES["invalid"]]},
            ),
            (
                {
                    "email": "user😊@email.com",
                    "password": "contraseñaUser123",
                    "confirm_password": "contraseñaUser123",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"email": [ERROR_MESSAGES["invalid"]]},
            ),
            (
                {
                    "email": "user1@email com",
                    "password": "contraseñaUser123",
                    "confirm_password": "contraseñaUser123",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"email": [ERROR_MESSAGES["invalid"]]},
            ),
        ],
    )
    def test_if_email_invalid(
        self,
        request_data: Dict[str, Dict[str, Any]],
        messages_expected: Dict[str, Any],
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is invalid and does not exist in the database.
        """

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=request_data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "invalid_request_data"

        # Asserting that the error messages are correct
        errors_formated = format_serializer_errors(data=response.data["detail"])

        for field, messages in messages_expected.items():
            if isinstance(messages, dict):
                diff = DeepDiff(
                    t1=errors_formated[field],
                    t2=messages,
                    ignore_order=True,
                )
                assert not bool(diff)
            else:
                obtained = {*errors_formated[field]}
                expected = {*messages}

                assert bool(obtained.symmetric_difference(expected)) is False

    @pytest.mark.parametrize(
        argnames="request_data, messages_expected",
        argvalues=[
            (
                {
                    "email": "user1@email.com",
                    "password": "password123",
                    "confirm_password": "password123",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"password": [ERROR_MESSAGES["password_common"]]},
            ),
            (
                {
                    "email": "user1@email.com",
                    "password": "5165156561561",
                    "confirm_password": "5165156561561",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {"password": [ERROR_MESSAGES["password_no_upper_lower"]]},
            ),
        ],
        ids=[
            "common_password",
            "no_upper_lower_password",
        ],
    )
    def test_if_password_invalid(
        self,
        request_data: Dict[str, Dict[str, Any]],
        messages_expected: Dict[str, Any],
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is invalid and does not exist in the database.
        """

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=request_data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "invalid_request_data"

        # Asserting that the error messages are correct
        errors_formated = format_serializer_errors(data=response.data["detail"])

        for field, messages in messages_expected.items():
            if isinstance(messages, dict):
                diff = DeepDiff(
                    t1=errors_formated[field],
                    t2=messages,
                    ignore_order=True,
                )
                assert not bool(diff)
            else:
                obtained = {*errors_formated[field]}
                expected = {*messages}

                assert bool(obtained.symmetric_difference(expected)) is False

    @pytest.mark.parametrize(
        argnames="registration_data, request_data, messages_expected",
        argvalues=[
            (
                {
                    "email": "user1@email.com",
                    "password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {
                    "email": "user1@email.com",
                    "password": "hjAUYS68AdfgK",
                    "confirm_password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia 1",
                    "phone_number": "+593991111112",
                    "ruc": "1234567890124",
                    "address": "Mi compañia 1",
                },
                {"email": [ERROR_MESSAGES["email_in_use"]]},
            ),
            (
                {
                    "email": "user1@email.com",
                    "password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {
                    "email": "user2@email.com",
                    "password": "hjAUYS68AdfgK",
                    "confirm_password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111112",
                    "ruc": "1234567890124",
                    "address": "Mi compañia 1",
                },
                {"name": [ERROR_MESSAGES["first_name_in_use"]]},
            ),
            (
                {
                    "email": "user1@email.com",
                    "password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {
                    "email": "user2@email.com",
                    "password": "hjAUYS68AdfgK",
                    "confirm_password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia 1",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890124",
                    "address": "Mi compañia 1",
                },
                {"phone_number": [ERROR_MESSAGES["phone_in_use"]]},
            ),
            (
                {
                    "email": "user1@email.com",
                    "password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia",
                    "phone_number": "+593991111111",
                    "ruc": "1234567890123",
                    "address": "Mi compañia",
                },
                {
                    "email": "user2@email.com",
                    "password": "hjAUYS68AdfgK",
                    "confirm_password": "hjAUYS68AdfgK",
                    "name": "Nombre de la compañia 1",
                    "phone_number": "+593991111112",
                    "ruc": "1234567890123",
                    "address": "Mi compañia 1",
                },
                {"ruc": [ERROR_MESSAGES["cc_ruc_in_use"]]},
            ),
        ],
        ids=[
            "email_in_use",
            "name_in_use",
            "phone_in_use",
            "ruc_in_use",
        ],
    )
    def test_data_used(
        self,
        registration_data: Dict[str, Dict[str, Any]],
        request_data: Dict[str, Dict[str, Any]],
        messages_expected: Dict[str, Any],
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when the request data is invalid and exists in the database.
        """

        # Creating the user data to be used in the test
        self.user_factory.create_user(
            user_role=COMPANY_ROLE,
            data=registration_data,
            save=True,
        )

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=request_data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["code"] == "invalid_request_data"

        # Asserting that the error messages are correct
        errors_formated = format_serializer_errors(data=response.data["detail"])

        for field, messages in messages_expected.items():
            if isinstance(messages, dict):
                diff = DeepDiff(
                    t1=errors_formated[field],
                    t2=messages,
                    ignore_order=True,
                )
                assert not bool(diff)
            else:
                obtained = {*errors_formated[field]}
                expected = {*messages}

                assert bool(obtained.symmetric_difference(expected)) is False

    @patch(
        target="apps.users.applications.UseCaseRegisterUser.create_company",
        side_effect=DatabaseConnectionAPIError,
    )
    def test_if_conection_db_failed(
        self,
        create_method_mock: Mock,
        client: Client,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        view when a DatabaseConnectionAPIError exception is raised.
        """

        # Creating the user data to be used in the test
        user_factory_obj = self.user_factory.create_user(user_role=COMPANY_ROLE)
        data = user_factory_obj.data
        base_data = data["base_data"]
        role_data = data["role_data"]
        base_data["confirm_password"] = base_data["password"]
        request_data = {**base_data, **role_data}

        # Simulating the request
        response = client.post(
            path=reverse(viewname=self.path_name),
            data=request_data,
            content_type="application/json",
        )

        # Asserting that response data is correct
        status_code_expected = DatabaseConnectionAPIError.status_code
        response_code_expected = DatabaseConnectionAPIError.default_code
        response_data_expected = DatabaseConnectionAPIError.default_detail

        assert response.status_code == status_code_expected
        assert response.data["code"] == response_code_expected
        assert response.data["detail"] == response_data_expected
