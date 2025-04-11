from apps.users.domain.interfaces import IUserRepository
from apps.users.domain.entities import User
from apps.users.domain.constants import (
    BASE_USER_MODEL,
    NATURAL_PERSON_MODEL,
    COMPANY_MODEL,
    ADMIN_MODEL,
)
from apps.exceptions import DatabaseConnectionAPIError
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError
from django.db.models import Model, QuerySet
from typing import Dict, Tuple, Any


class UserRepository(IUserRepository):
    """
    A repository class for managing `User` entity in the database.

    This class provides methods that perform CRUD operations among other types
    of queries. It handles operational errors in the database by generating a
    custom exception.
    """

    model = User

    @classmethod
    def create_user(cls, data: Dict[str, Any], user_role: str) -> User:

        try:
            return cls.model.objects.create_user(
                user_role=user_role,
                base_data=data["base_data"],
                role_data=data["role_data"],
            )
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def get_user(
        cls,
        filters: Dict[str, Any],
        get_role_data: str = None,
    ) -> QuerySet[User]:

        try:
            if "email" in filters:
                filters["email"] = cls.model.objects.normalize_email(
                    email=filters["email"]
                )

            query = cls.model.objects.filter(**filters).defer("date_joined")

            if get_role_data is not None:
                return query.prefetch_related(get_role_data)

            return query
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def update_user(
        cls,
        base_user_instance: User = None,
        user_role_instance: Model = None,
        base_data: Dict[str, Any] = None,
        role_data: Dict[str, Any] = None,
    ) -> Tuple[User, Model]:

        try:
            if base_data is not None and base_user_instance is not None:
                for field, value in base_data.items():
                    setattr(base_user_instance, field, value)

                base_user_instance.save()
            if role_data is not None and user_role_instance is not None:
                for field, value in role_data.items():
                    setattr(user_role_instance, field, value)

                user_role_instance.save()

            return base_user_instance, user_role_instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def exists(cls, model_name: str, data: Dict[str, Any]) -> bool:

        try:
            if model_name == BASE_USER_MODEL:
                if "email" in data:
                    data["email"] = cls.model.objects.normalize_email(
                        email=data["email"]
                    )

                return cls.model.objects.filter(**data).exists()
            elif model_name not in [
                NATURAL_PERSON_MODEL,
                COMPANY_MODEL,
                ADMIN_MODEL,
            ]:
                raise ValueError("Invalid model name provided.")

            content_type = ContentType.objects.get(model=model_name)
            related_model = content_type.model_class()

            return related_model.objects.filter(**data).exists()
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()
