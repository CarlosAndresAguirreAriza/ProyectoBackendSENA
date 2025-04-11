from apps.authentication.domain.typing import JSONWebToken, JWTPayload
from apps.authentication.domain.constants import ACCESS_TOKEN_LIFETIME
from apps.authentication.domain.entities import JWT, JWTBlacklist
from apps.authentication.jwt import AccessToken
from apps.users.domain.constants import NATURAL_PERSON_ROLE
from apps.users.domain.entities import User
from tests.utils import fake
from settings.environments.base import SIMPLE_JWT
from rest_framework_simplejwt.utils import (
    aware_utcnow,
    datetime_to_epoch,
    datetime_from_epoch,
)
from datetime import datetime
from jwt import encode
from uuid import uuid4
from typing import Tuple


class JWTFactory:
    """
    Factory class for creating and managing JSON Web Tokens (JWTs) for use in
    testing.

    This class provides methods for generating JWTs with specific payloads, saving
    them to the database, managing their lifecycle, including adding them to a
    blacklist for invalidation.
    """

    __jwt_model = JWT
    __blacklist_model = JWTBlacklist
    token: JSONWebToken = None
    payload: JWTPayload = None

    @classmethod
    def create_token(
        cls,
        token_type: str,
        user: User = None,
        exp: bool = False,
        save: bool = False,
        add_blacklist: bool = False,
        invalid: bool = False,
    ) -> "JWTFactory":
        """
        Creates an token with the provided parameters.

        #### Parameters:
        - user: The user to whom the token belongs.
        - exp: Whether the token should be expired.
        - save: Whether to save the token in the database.
        - add_blacklist: Whether to add the token to the blacklist.
        - invalid: Whether the token should be invalid.
        """

        map_creation_method = {AccessToken.token_type: cls.__create_access_token}
        payload, token_encoded = map_creation_method[token_type](
            add_blacklist=add_blacklist,
            invalid=invalid,
            user=user,
            save=save,
            exp=exp,
        )
        cls.token = token_encoded
        cls.payload = payload

        return cls

    @classmethod
    def __create_access_token(
        cls,
        user: User,
        exp: bool,
        save: bool,
        add_blacklist: bool,
        invalid: bool,
    ) -> Tuple[JWTPayload, JSONWebToken]:
        """
        Creates an access token with the provided parameters.

        #### Parameters:
        - user: The user to whom the token belongs.
        - exp: Whether the token should be expired.
        - save: Whether to save the token in the database.
        - add_blacklist: Whether to add the token to the blacklist.
        - invalid: Whether the token should be invalid.
        """

        if invalid is True:
            token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNzA5MDkxZjY1MDlU3IiwidXNlcl9pZCI6IjUwNTI5MjBjLWE3ZDYtNDM4ZS1iZmQwLWVhNTUyMTM4ODM2YrCZDFxbgBxhvNBJZsLzsyCn5pabwKKKSX9VKmQ8g"

            return None, token

        exp_token = (
            aware_utcnow() - ACCESS_TOKEN_LIFETIME
            if exp
            else aware_utcnow() + ACCESS_TOKEN_LIFETIME
        )
        user_instance = user or cls.__create_user()

        return cls.__create(
            token_type=AccessToken.token_type,
            add_blacklist=add_blacklist,
            user=user_instance,
            exp=exp_token,
            save=save,
        )

    @classmethod
    def __create(
        cls,
        save: bool,
        user: User,
        token_type: str,
        add_blacklist: bool,
        exp: datetime,
    ) -> Tuple[JWTPayload, JSONWebToken]:
        """
        Creates a token with the provided parameters.

        #### Parameters:
        - save: Whether to save the token in the database.
        - user: The user to whom the token belongs.
        - token_type: The type of token to create.
        - add_blacklist: Whether to add the token to the blacklist.
        - exp: The expiration date of the token.
        """

        token_payload = cls.__get_payload(
            token_type=token_type,
            user=user,
            exp=exp,
        )
        token = encode(
            payload=token_payload,
            key=SIMPLE_JWT["SIGNING_KEY"],
            algorithm=SIMPLE_JWT["ALGORITHM"],
        )

        if save is True:
            token_instance = cls.__save(
                payload=token_payload,
                token=token,
                user=user,
            )

            if add_blacklist is True:
                cls.__add_blacklist(token=token_instance)

        return token_payload, token

    @staticmethod
    def __get_payload(
        token_type: str,
        exp: datetime,
        user: User,
    ) -> JWTPayload:
        """
        Creates the payload for a token.

        #### Parameters:
        - token_type: The type of token to create.
        - exp: The expiration date of the token.
        - user: The user to whom the token belongs.
        """

        return {
            "token_type": token_type,
            "exp": datetime_to_epoch(dt=exp),
            "iat": datetime_to_epoch(dt=aware_utcnow()),
            "jti": uuid4().hex,
            "user_uuid": user.uuid.__str__(),
            "user_role": user.role,
        }

    @classmethod
    def __save(cls, user: User, payload: JWTPayload, token: JSONWebToken) -> JWT:
        """
        Saves the token in the database.

        #### Parameters:
        - user: The user to whom the token belongs.
        - payload: The payload of the token.
        - token: The token to be saved.
        """

        return cls.__jwt_model.objects.create(
            expires_at=datetime_from_epoch(ts=payload["exp"]),
            jti=payload["jti"],
            token=token,
            user=user,
        )

    @classmethod
    def __add_blacklist(cls, token: JWT) -> None:
        """
        Invalidates a JSON Web Token by adding it to the blacklist.

        #### Parameters:
        - token: The token to be invalidated.
        """

        cls.__blacklist_model.objects.create(token=token)

    @staticmethod
    def __create_user() -> User:
        """This method creates a user with fake data."""

        data = {}
        data.setdefault("is_staff", False)
        data.setdefault("is_superuser", False)
        data.setdefault("is_active", True)
        data.setdefault("is_deleted", False)

        user = User(
            email=fake.email(),
            role=NATURAL_PERSON_ROLE,
            **data,
        )
        user.set_password(raw_password=fake.password())

        return user
