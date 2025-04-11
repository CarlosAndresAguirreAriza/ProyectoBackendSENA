from apps.authentication.domain.entities import JWT, JWTBlacklist
from apps.authentication.domain.typing import JSONWebToken, JWTPayload
from apps.authentication.domain.interfaces import IJWTRepository
from apps.users.domain.entities import User
from apps.exceptions import DatabaseConnectionAPIError
from rest_framework_simplejwt.utils import datetime_from_epoch
from django.db import OperationalError
from django.db.models import QuerySet
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass(init=False)
class JWTRepository(IJWTRepository):
    """
    A repository class for managing `JWT` and `JWTBlacklist` entities in the
    database.

    This class provides methods that perform CRUD operations among other types
    of queries. It handles operational errors in the database by generating a
    custom exception.
    """

    __jwt_model = JWT
    __blacklist_model = JWTBlacklist

    @classmethod
    def get_token(cls, filters: Dict[str, Any]) -> QuerySet[JWT]:

        try:
            # fmt: off
            return (
                cls.__jwt_model.objects
                .filter(**filters)
                .defer("id", "date_joined")
                .select_related("user")
            )
            # fmt: on
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def add_checklist(
        cls,
        token: JSONWebToken,
        payload: JWTPayload,
        user: User,
    ) -> None:

        try:
            cls.__jwt_model.objects.create(
                jti=payload["jti"],
                token=token,
                user=user,
                expires_at=datetime_from_epoch(ts=payload["exp"]),
            )
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def add_blacklist(cls, token: JWT) -> None:

        try:
            cls.__blacklist_model.objects.create(token=token)
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def exists_blacklist(cls, jti: str) -> bool:

        try:
            return cls.__blacklist_model.objects.filter(token__jti=jti).exists()
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()
