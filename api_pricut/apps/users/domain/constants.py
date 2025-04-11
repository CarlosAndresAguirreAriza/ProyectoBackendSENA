from enum import Enum


class BaseUserDataProperties(Enum):
    """Define the data properties of a base user."""

    MODEL = "user"
    EMAIL_MAX_LENGTH = 40
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 20


BASE_USER_MODEL = BaseUserDataProperties.MODEL.value


class NaturalPersonDataProperties(Enum):
    """Define the data properties of a natural person user."""

    MODEL = "naturalpersonrole"
    BASE_DATA = ["email", "password"]
    ROLE_DATA = [
        "first_name",
        "last_name",
        "cc",
        "phone_number",
        "address",
    ]
    FIRST_NAME_MAX_LENGTH = 25
    LAST_NAME_MAX_LENGTH = 25
    CC_MAX_LENGTH = 10
    PHONE_NUMBER_MAX_LENGTH = 19
    ADDRESS_MAX_LENGTH = 40


NATURAL_PERSON_MODEL = NaturalPersonDataProperties.MODEL.value


class CompanyDataProperties(Enum):
    """Define the data properties of a company user."""

    MODEL = "companyrole"
    BASE_DATA = ["email", "password"]
    ROLE_DATA = [
        "name",
        "ruc",
        "phone_number",
        "address",
    ]
    NAME_MAX_LENGTH = 40
    RUC_MAX_LENGTH = 13
    PHONE_NUMBER_MAX_LENGTH = 19
    ADDRESS_MAX_LENGTH = 40


COMPANY_MODEL = CompanyDataProperties.MODEL.value


class AdminDataProperties(Enum):
    """Define the data properties of a admin user."""

    MODEL = "adminrole"
    BASE_DATA = ["email", "password"]
    ROLE_DATA = ["first_name", "last_name"]
    FIRST_NAME_MAX_LENGTH = 25
    LAST_NAME_MAX_LENGTH = 25


ADMIN_MODEL = AdminDataProperties.MODEL.value


class UserRoles(Enum):
    """This enum represents the roles that a user can have."""

    NATURAL_PERSON = NATURAL_PERSON_MODEL
    COMPANY = COMPANY_MODEL
    ADMIN = ADMIN_MODEL


NATURAL_PERSON_ROLE = UserRoles.NATURAL_PERSON.value
COMPANY_ROLE = UserRoles.COMPANY.value
ADMIN_ROLE = UserRoles.ADMIN.value


USER_PERMISSIONS = {
    "view_base_data": f"users.view_{BASE_USER_MODEL}",
    "change_base_data": f"users.change_{BASE_USER_MODEL}",
    "delete_base_data": f"users.delete_{BASE_USER_MODEL}",
    "view_naturalperson": f"users.view_{NATURAL_PERSON_MODEL}",
    "change_naturalperson": f"users.change_{NATURAL_PERSON_MODEL}",
    "delete_naturalperson": f"users.delete_{NATURAL_PERSON_MODEL}",
    "view_company": f"users.view_{COMPANY_MODEL}",
    "change_company": f"users.change_{COMPANY_MODEL}",
    "delete_company": f"users.delete_{COMPANY_MODEL}",
    "view_admin": f"users.view_{ADMIN_MODEL}",
}
