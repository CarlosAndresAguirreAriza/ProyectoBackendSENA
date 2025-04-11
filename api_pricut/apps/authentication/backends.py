from apps.users.infrastructure.repositories import UserRepository
from apps.users.domain.entities import User
from rest_framework.request import Request
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """
    A `custom authentication backend` that authenticates users based on their email
    and password.
    """

    user_repository = UserRepository

    def authenticate(
        self,
        request: Request,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate a user with the given email and password.

        #### Parameters:
        - request: The request object.
        - email: The email of the user.
        - password: The password of the user.
        """

        user = self.user_repository.get_user(filters={"email": email}).first()

        if user is None:
            return None

        return user if user.check_password(raw_password=password) else None
