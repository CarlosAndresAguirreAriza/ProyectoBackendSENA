from apps.users.infrastructure.serializers import (
    RegisterCompanySerializer as Serializer,
)
from apps.users.domain.constants import (
    CompanyDataProperties,
    BaseUserDataProperties,
)
from apps.exceptions import DatabaseConnectionAPIError
from apps.utils import ERROR_MESSAGES
from drf_spectacular.utils import (
    extend_schema_serializer,
    extend_schema,
    OpenApiResponse,
    OpenApiExample,
)


# Company and base user properties
EMAIL_MAX_LENGTH = BaseUserDataProperties.EMAIL_MAX_LENGTH.value
PASSWORD_MAX_LENGTH = BaseUserDataProperties.PASSWORD_MAX_LENGTH.value
PASSWORD_MIN_LENGTH = BaseUserDataProperties.PASSWORD_MIN_LENGTH.value
NAME_MAX_LENGTH = CompanyDataProperties.NAME_MAX_LENGTH.value
RUC_MAX_LENGTH = CompanyDataProperties.RUC_MAX_LENGTH.value
ADDRESS_MAX_LENGTH = CompanyDataProperties.ADDRESS_MAX_LENGTH.value
PHONE_NUMBER_MAX_LENGTH = CompanyDataProperties.PHONE_NUMBER_MAX_LENGTH.value


RegisterCompanySerializerSchema = extend_schema_serializer(
    examples=[
        OpenApiExample(
            name="data_valid",
            summary="Register a new user with role company.",
            description=f"A valid user registration data. The following validations will be applied:\n- **Name:** This field is required, must not exceed {NAME_MAX_LENGTH} characters, and must not be in use.\n- **Single Taxpayer Registry (RUC):** This field is required, must be exactly {RUC_MAX_LENGTH} characters long, and must not be in use.\n- **Address:** This field is required, has a maximum of {ADDRESS_MAX_LENGTH} characters, and must not be in use.\n- **Phone number:** This field is required and must be a valid phone number in E164 format, with a maximum of {PHONE_NUMBER_MAX_LENGTH} characters, that is not in use.\n- **Email:** This field is required and must not exceed {EMAIL_MAX_LENGTH} characters, must follow standard email format, and must not be in use.\n- **Password:** This field is required and must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters long, it must not be an easy-to-guess password, and it cannot contain too much of the user's personal information. It should not be a common password or contain only numbers. \n- **Confirm password:** This field is required and should match the password field.\n\nFields other than those defined for this request are not allowed.",
            value={
                "name": "Compañia 1",
                "ruc": "1234567890123",
                "phone_number": "+593991111111",
                "address": "Mi Compañia",
                "email": "user1@email.com",
                "password": "contraseña16545641",
                "confirm_password": "contraseña16545641",
            },
            request_only=True,
        ),
    ],
)


@RegisterCompanySerializerSchema
class RegisterCompanySerializer(Serializer):
    pass


CreateCompanySchema = extend_schema(
    operation_id="create_company",
    tags=["Users"],
    request=RegisterCompanySerializer,
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
                            "name": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["first_name_in_use"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=NAME_MAX_LENGTH
                                ),
                            ],
                            "ruc": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["cc_ruc_in_use"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=RUC_MAX_LENGTH
                                ),
                            ],
                            "phone_number": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["phone_numbers_in_use"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=PHONE_NUMBER_MAX_LENGTH
                                ),
                            ],
                            "address": [
                                ERROR_MESSAGES["required"],
                                ERROR_MESSAGES["blank"],
                                ERROR_MESSAGES["null"],
                                ERROR_MESSAGES["invalid"],
                                ERROR_MESSAGES["max_length"].format(
                                    max_length=ADDRESS_MAX_LENGTH
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
