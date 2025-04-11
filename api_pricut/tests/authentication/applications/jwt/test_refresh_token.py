from apps.authentication.applications import UseCaseRefreshToken
from apps.authentication.jwt import AccessToken
from apps.authentication.domain.entities import JWT
from apps.users.infrastructure.repositories import UserRepository
from apps.users.domain.constants import NATURAL_PERSON_ROLE, COMPANY_ROLE
from apps.users.domain.entities import User
from apps.exceptions import (
    DatabaseConnectionAPIError,
    JWTAPIError,
)
from settings.environments.base import SIMPLE_JWT
from tests.factories import JWTFactory, UserFactory
from tests.utils import empty_queryset
from unittest.mock import Mock
from jwt import decode
import pytest


@pytest.mark.django_db
class TestUseCaseRefreshToken:
    """
    This class encapsulates all the tests of the JWT use case responsible for
    updating the tokens of a user.

    #### Clarifications:
    - The execution of this logic does not depend on the user's permissions; that is,
    the user's permissions are not validated.
    """

    application_class = UseCaseRefreshToken
    user_factory = UserFactory
    jwt_factory = JWTFactory

    @pytest.mark.parametrize(
        argnames="user_role",
        argvalues=[NATURAL_PERSON_ROLE, COMPANY_ROLE],
        ids=[f"{NATURAL_PERSON_ROLE}_user", f"{COMPANY_ROLE}_user"],
    )
    def test_updated_tokens(self, user_role: str) -> None:
        """
        This test case is responsible for testing the successful update of the tokens
        of a user.
        """

        # Creating the JWTs to be used in the test
        user_factory_obj = self.user_factory.create_user(
            user_role=user_role,
            save=True,
        )
        jwt_factory_obj = self.jwt_factory.create_token(
            token_type=AccessToken.token_type,
            user=user_factory_obj.user,
            save=True,
        )

        # Instantiating the application and calling the method
        use_case = self.application_class(user_repository=UserRepository)
        new_access_token = use_case.refresh_token(
            access_token=AccessToken(token=jwt_factory_obj.token)
        )

        # Assert that the generated tokens were saved in the database
        payload = decode(
            jwt=new_access_token,
            key=SIMPLE_JWT["SIGNING_KEY"],
            algorithms=[SIMPLE_JWT["ALGORITHM"]],
        )
        token_instance = (
            JWT.objects.filter(jti=payload["jti"]).select_related("user").first()
        )

        assert token_instance is not None

        # Asserting that the tokens were created with the correct data
        assert str(token_instance.user.uuid) == payload["user_uuid"]
        assert token_instance.jti == payload["jti"]
        assert token_instance.token == new_access_token
        assert payload["user_role"] == user_role

    @pytest.mark.parametrize(
        argnames="token",
        argvalues=[
            JWTFactory.create_token(token_type=AccessToken.token_type).token
        ],
        ids=["valid_token"],
    )
    def test_if_user_not_found(self, token: str) -> None:
        """
        This test is responsible for validating the expected behavior of the use case
        when the user is not found in the database.
        """

        # Mocking the methods
        user_repository = Mock()
        get_user: Mock = user_repository.get_user
        get_user.return_value = empty_queryset(model=User)

        # Instantiating the application
        with pytest.raises(JWTAPIError):
            app = self.application_class(user_repository=user_repository)
            app.refresh_token(access_token=AccessToken(token=token))

        # Asserting that the tokens were not generated
        assert JWT.objects.count() == 0

    @pytest.mark.parametrize(
        argnames="token",
        argvalues=[
            JWTFactory.create_token(token_type=AccessToken.token_type).token
        ],
        ids=["valid_token"],
    )
    def test_if_conection_db_failed(self, token: str) -> None:
        """
        Test that validates the expected behavior of the use case when the connection
        to the database fails.
        """

        # Mocking the methods
        user_repository = Mock()
        get_user: Mock = user_repository.get_user
        get_user.side_effect = DatabaseConnectionAPIError

        # Instantiating the application
        with pytest.raises(DatabaseConnectionAPIError):
            app = self.application_class(user_repository=user_repository)
            app.refresh_token(access_token=AccessToken(token=token))

        # Asserting that the tokens were not generated
        assert JWT.objects.count() == 0
