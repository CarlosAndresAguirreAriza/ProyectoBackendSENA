from apps.users.infrastructure.serializers import (
    RegisterNaturalPersonSerializer as Serializer,
)
from apps.users.domain.constants import (
    NaturalPersonDataProperties,
    BaseUserDataProperties,
    NATURAL_PERSON_ROLE,
)
from apps.exceptions import DatabaseConnectionAPIError
from apps.utils import ERROR_MESSAGES
from drf_spectacular.utils import (
    extend_schema_serializer,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)


# Natural person and base user properties
EMAIL_MAX_LENGTH = BaseUserDataProperties.EMAIL_MAX_LENGTH.value
PASSWORD_MAX_LENGTH = BaseUserDataProperties.PASSWORD_MAX_LENGTH.value
PASSWORD_MIN_LENGTH = BaseUserDataProperties.PASSWORD_MIN_LENGTH.value
FIRST_NAME_MAX_LENGTH = NaturalPersonDataProperties.FIRST_NAME_MAX_LENGTH.value
LAST_NAME_MAX_LENGTH = NaturalPersonDataProperties.LAST_NAME_MAX_LENGTH.value


RegisterNaturalPersonSerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary=f"Register a new user with role {NATURAL_PERSON_ROLE}.",
            description=f"A valid user registration data. The following validations will be applied:\n- **First name and last name:** These fields are required; they must not exceed {FIRST_NAME_MAX_LENGTH} characters, must contain only letters and spaces, and must not be in use.\n- **Email:** This field is required and must not exceed {EMAIL_MAX_LENGTH} characters, must follow standard email format, and must not be in use.\n- **Password:** This field is required and must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters long, it must not be an easy-to-guess password, and it cannot contain too much of the user's personal information. It should not be a common password or contain only numbers. \n- **Confirm password:** This field is required and should match the password field.\n\nFields other than those defined for this request are not allowed.",
            value={
                "first_name": "Nombres del usuario",
                "last_name": "Apellidos del usuario",
                "email": "user1@email.com",
                "password": "contraseña16545641",
                "confirm_password": "contraseña16545641",
            },
            request_only=True,
        ),
    ],
)


@RegisterNaturalPersonSerializerSchema
class RegisterNaturalPersonSerializer(Serializer):
    pass


CreateNaturalPersonSchema = extend_schema(
    operation_id="create_natural_person",
    tags=["Users"],
    request=RegisterNaturalPersonSerializer,
    responses={
        201: OpenApiResponse(
            description="**(CREATED)** User created successfully."
        ),
        400: OpenApiResponse(
            description="**(BAD_REQUEST)** The request data is invalid; error messages are returned for each field that failed validation. Some messages are in Spanish because they will be used in the frontend and visible to the user.",
            response={
                "properties": {
                    "code": {"type": "string"},
                    "detail": {"type": "object"},
                }
            },
            examples=[
                OpenApiExample(
                    name="invalid_data",
                    summary="Invalid data",
                    description="These are the possible error messages for each field.",
                    value={
                        "code": "invalid_request_data",
                        "detail": {
                            "email": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["email_in_use"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=EMAIL_MAX_LENGTH
                                ),
                            ],
                            "password": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["password_no_upper_lower"],
                                ERROR_MESSAGES["password_common"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=PASSWORD_MAX_LENGTH
                                ),
                                ERROR_MESSAGES["min_length"].format(
                                    min_length=PASSWORD_MIN_LENGTH
                                ),
                            ],
                            "confirm_password": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["password_mismatch"],
                            ],
                            "first_name": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["first_name_in_use"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=FIRST_NAME_MAX_LENGTH
                                ),
                            ],
                            "last_name": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["last_name_in_use"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=LAST_NAME_MAX_LENGTH
                                ),
                            ],
                        },
                    },
                ),
                OpenApiExample(
                    name="data_not_allowed",
                    summary="Data not allowed",
                    description="The request data contains an invalid field.",
                    value={
                        "code": "invalid_request_data",
                        "detail": {
                            "invalid_field": ["This field is not allowed."],
                        },
                    },
                ),
            ],
        ),
        500: OpenApiResponse(
            description="**(INTERNAL_SERVER_ERROR)** An unexpected error occurred.",
            response={
                "properties": {
                    "detail": {"type": "string"},
                    "code": {"type": "string"},
                }
            },
            examples=[
                OpenApiExample(
                    name="database_connection_error",
                    summary="Database connection error",
                    description="The connection to the database could not be established.",
                    value={
                        "code": DatabaseConnectionAPIError.default_code,
                        "detail": DatabaseConnectionAPIError.default_detail,
                    },
                ),
            ],
        ),
    },
)
