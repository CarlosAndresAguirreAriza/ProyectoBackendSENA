from django.core.management.base import BaseCommand
from apps.users.domain.constants import ADMIN_ROLE
from apps.users.domain.entities import User
from decouple import config
import os


CURRENT_SETTINGS = os.getenv("DJANGO_SETTINGS_MODULE")


class Command(BaseCommand):
    """Create admin user in development and production environment."""

    help = "Create admin user in development and production environment"
    __model = User

    def handle(self, *args, **kwargs):
        """
        Handle the command, create admin in development and production environment
        """

        self.stdout.write(
            msg=self.style.MIGRATE_HEADING(
                "Creating admin user, runtime environment: "
            )
            + self.style.MIGRATE_LABEL(CURRENT_SETTINGS)
        )

        if "development" in CURRENT_SETTINGS:
            self.__create_admin_dev()
        elif "production" in CURRENT_SETTINGS:
            self.__create_admin_prod()

    def __create_admin_dev(self) -> None:
        """Create admin in development environment."""

        email = config("ADMIN_DEV_EMAIL", cast=str)
        password = config("ADMIN_DEV_PASSWORD", cast=str)

        if not self.__model.objects.filter(email=email).exists():
            self.__model.objects.create_user(
                base_data={"email": email, "password": password},
                role_data={"first_name": "Admin", "last_name": "User"},
                user_role=ADMIN_ROLE,
            )
            self.stdout.write(
                msg=f"   Development administrator created with email {email}... "
                + self.style.SUCCESS("OK")
            )
        else:
            self.stdout.write(
                msg=f"   Development administrator with email {email}... "
                + self.style.WARNING("already exists")
            )

    def __create_admin_prod(self) -> None:
        """Create admin in production environment."""

        first_name = config("ADMIN_PROD_FIRST_NAME", cast=str)
        last_name = config("ADMIN_PROD_LAST_NAME", cast=str)
        email = config("ADMIN_PROD_EMAIL", cast=str)
        password = config("ADMIN_PROD_PASSWORD", cast=str)

        if not self.__model.objects.filter(email=email).exists():
            self.__model.objects.create_user(
                base_data={"email": email, "password": password},
                role_data={"first_name": first_name, "last_name": last_name},
                user_role=ADMIN_ROLE,
            )
            self.stdout.write(
                msg=f"   Production administrator created with email {email}... "
                + self.style.SUCCESS("OK")
            )
        else:
            self.stdout.write(
                msg=f"   Production administrator with email {email}... "
                + self.style.WARNING("already exists")
            )
