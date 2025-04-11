from apps.users.domain import constants
from apps.exceptions import DatabaseConnectionAPIError
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import (
    UserManager as BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
    Group,
)
from django.contrib.contenttypes.models import ContentType
from django.db import OperationalError, models
from typing import Dict, Any
from uuid import uuid4


# User data properties
BaseUser = constants.BaseUserDataProperties
NaturalPerson = constants.NaturalPersonDataProperties
Company = constants.CompanyDataProperties
Admin = constants.AdminDataProperties


class UserManager(BaseUserManager):
    """
    User model manager that provides methods for creating user instances with different
    roles, including superusers. It is also responsible for assigning the corresponding
    permissions according to the assigned role.
    """

    def create_user(
        self,
        user_role: str,
        base_data: Dict[str, Any],
        role_data: Dict[str, Any],
    ) -> "User":
        """
        Creates a user with the given data and assigns the corresponding permissions
        according to the assigned role.
        """

        user = self.__create_user(
            base_data=base_data,
            role_data=role_data,
            user_role=user_role,
        )
        self.__assign_permissions(user=user, user_role=user_role)

        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **base_data,
    ) -> "User":
        """Create and save a SuperUser with the given email and password."""

        base_data.setdefault("is_staff", True)
        base_data.setdefault("is_superuser", True)
        base_data.setdefault("is_active", True)

        if base_data.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        elif base_data.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        elif base_data.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")

        base_data["email"] = email
        base_data["password"] = password

        return self.__create_user(base_data=base_data)

    def __create_user(
        self,
        base_data: Dict[str, Any],
        role_data: Dict[str, Any] = None,
        user_role: str = None,
    ) -> "User":
        """
        This is a private method that handles the creation of a user instance.
        Optionally it can associate to a model instance that encapsulates the user
        role data if `related_model_name` and `role_data` are provided.
        """

        email = base_data.pop("email")
        password = base_data.pop("password")
        user: "User" = self.model(
            email=self.normalize_email(email),
            role=user_role,
            **base_data,
        )
        user.set_password(raw_password=password)
        user.save(using=self._db)

        if user_role is not None and role_data is not None:
            related_model = ContentType.objects.get(model=user_role).model_class()
            related_model.objects.create(base_data=user, **role_data)

        return user

    @staticmethod
    def __assign_permissions(user: "User", user_role: str) -> None:
        """Assign permissions to the user."""

        try:
            group = Group.objects.get(name=user_role)
        except OperationalError:
            raise DatabaseConnectionAPIError()

        user.groups.add(group)
        user.save()


class User(AbstractBaseUser, PermissionsMixin):
    """
    This object encapsulates the `base data` of a user, which is essential for
    authentication, permission validation and security processes.
    """

    uuid = models.UUIDField(
        db_column="uuid",
        default=uuid4,
        primary_key=True,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        db_column="email",
        max_length=BaseUser.EMAIL_MAX_LENGTH.value,
        unique=True,
        null=False,
        blank=False,
        db_index=True,
    )
    password = models.CharField(
        db_column="password",
        max_length=128,
        null=False,
        blank=False,
    )
    role = models.CharField(
        db_column="role",
        max_length=60,
        null=True,
        blank=False,
    )
    is_staff = models.BooleanField(
        db_column="is_staff",
        null=False,
        blank=False,
        default=False,
    )
    is_superuser = models.BooleanField(
        db_column="is_superuser",
        null=False,
        blank=False,
        default=False,
    )
    is_active = models.BooleanField(
        db_column="is_active",
        null=False,
        blank=False,
        default=False,
    )
    is_deleted = models.BooleanField(
        db_column="is_deleted",
        null=False,
        blank=False,
        default=False,
    )
    deleted_at = models.DateTimeField(
        db_column="deleted_at",
        null=True,
        blank=True,
    )
    last_login = models.DateTimeField(
        db_column="last_login",
        null=True,
        blank=True,
    )
    date_joined = models.DateTimeField(
        db_column="date_joined",
        auto_now_add=True,
    )

    objects: UserManager = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users.users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.email


class NaturalPersonRole(models.Model):
    """This object encapsulates the `role data` of a natural person user."""

    uuid = models.UUIDField(
        db_column="uuid",
        default=uuid4,
        primary_key=True,
    )
    base_data = models.OneToOneField(
        to="User",
        to_field="uuid",
        on_delete=models.CASCADE,
        related_name=constants.NATURAL_PERSON_MODEL,
        null=True,
    )
    first_name = models.CharField(
        db_column="first_name",
        max_length=NaturalPerson.FIRST_NAME_MAX_LENGTH.value,
        default="No tiene",
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        db_column="last_name",
        max_length=NaturalPerson.LAST_NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
    )
    cc = models.CharField(
        db_column="cc",
        max_length=NaturalPerson.CC_MAX_LENGTH.value,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )
    phone_number = PhoneNumberField(
        db_column="phone_number",
        max_length=NaturalPerson.PHONE_NUMBER_MAX_LENGTH.value,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )
    address = models.CharField(
        db_column="address",
        max_length=NaturalPerson.ADDRESS_MAX_LENGTH.value,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "users.natural_person_role"
        verbose_name = "Natural person role"
        verbose_name_plural = "Natural persons role"

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.uuid.__str__()

    def get_full_name(self) -> str:
        """Return the full name of the user."""

        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"


class CompanyRole(models.Model):
    """This object encapsulates the `role data` of a company user."""

    uuid = models.UUIDField(
        db_column="uuid",
        default=uuid4,
        primary_key=True,
    )
    base_data = models.OneToOneField(
        to="User",
        to_field="uuid",
        on_delete=models.CASCADE,
        related_name=constants.COMPANY_MODEL,
        null=True,
    )
    name = models.CharField(
        db_column="name",
        max_length=Company.NAME_MAX_LENGTH.value,
        unique=True,
        null=False,
        blank=False,
    )
    ruc = models.CharField(
        db_column="ruc",
        max_length=Company.RUC_MAX_LENGTH.value,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )
    phone_number = PhoneNumberField(
        db_column="phone_number",
        max_length=Company.PHONE_NUMBER_MAX_LENGTH.value,
        null=True,
        blank=True,
        unique=True,
        db_index=True,
    )
    address = models.CharField(
        db_column="address",
        max_length=Company.ADDRESS_MAX_LENGTH.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = "users.company_role"
        verbose_name = "Company role"
        verbose_name_plural = "Companies role"

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.uuid.__str__()


class AdminRole(models.Model):
    """This object encapsulates the `role data` of an admin user."""

    uuid = models.UUIDField(
        db_column="uuid",
        default=uuid4,
        primary_key=True,
    )
    base_data = models.OneToOneField(
        to="User",
        to_field="uuid",
        on_delete=models.CASCADE,
        related_name=constants.ADMIN_MODEL,
        null=True,
    )
    first_name = models.CharField(
        db_column="first_name",
        max_length=Admin.FIRST_NAME_MAX_LENGTH.value,
        default="No tiene",
        null=False,
        blank=False,
    )
    last_name = models.CharField(
        db_column="last_name",
        max_length=Admin.LAST_NAME_MAX_LENGTH.value,
        null=False,
        blank=False,
    )

    class Meta:
        db_table = "users.admin_role"
        verbose_name = "Admin role"
        verbose_name_plural = "Admins role"

    def __str__(self) -> str:
        """Return the string representation of the model."""

        return self.uuid.__str__()

    def get_full_name(self) -> str:
        """Return the full name of the user."""

        return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
