from apps.exceptions import NotAuthenticatedAPIError, PermissionDeniedAPIError
from rest_framework.serializers import Serializer
from rest_framework.request import Request
from rest_framework.permissions import BasePermission
from rest_framework.generics import GenericAPIView
from typing import Dict, List, Any, Callable
from enum import Enum
import unicodedata
import re


ERROR_MESSAGES = {
    # Length errors
    "max_length": "El valor ingresado no puede tener más de {max_length} caracteres.",
    "min_length": "El valor ingresado debe tener al menos {min_length} caracteres.",
    "max_value": "El valor ingresado no puede ser mayor a {max_value}.",
    "min_value": "El valor ingresado no puede ser menor a {min_value}.",
    "max_digits": "El valor ingresado no puede tener más de {max_digits} dígitos.",
    "max_length_list": "No puedes agregar o seleccionar más de {max_length} elementos.",
    "min_length_list": "Debes agregar o seleccionar al menos {min_length} elementos.",
    "max_whole_digits": "Asegúrese de que no haya más de {max_whole_digits} dígitos antes del punto decimal.",
    "decimal_places": "El valor ingresado no puede tener más de {decimal_places} decimales.",
    "empty": "Debes agregar o seleccionar al menos un elemento.",
    # Password errors
    "password_mismatch": "Las contraseñas no coinciden.",
    "password_common": "La contraseña que ha elegido es demasiado común y fácil de adivinar.",
    "password_no_upper_lower": "La contraseña debe contener al menos una mayuscula o una minuscula.",
    # Invalid data
    "invalid": "El valor ingresado es inválido.",
    "invalid_choice": "{input} no es una elección válida.",
    "invalid_url": "Introduzca una URL válida.",
    "not_a_dict": "Se esperaba un diccionario o JSON de elementos pero se obtuvo un dato de tipo ({input_type}).",
    "features_highlights": "Las funciones destacadas deben tener un título y una imagen.",
    "compatibility_cut": "Debe haber al menos una técnica de corte compatible, o puede considerar no agregar o eliminar este grosor del material.",
    "invalid_field": "Este campo no está permitido.",
    # Required fields
    "required": "Este campo es requerido.",
    "blank": "Este campo no puede estar en blanco.",
    "null": "Este campo no puede ser nulo.",
    # Data in use
    "cut_exists": "Ya existe un servicio con este nombre.",
    "material_exists": "Ya existe un material con este nombre.",
    "email_in_use": "Este correo electrónico ya está en uso.",
    "phone_in_use": "Este número de teléfono ya está en uso.",
    "first_name_in_use": "Esta nombre ya está en uso.",
    "last_name_in_use": "Este apellido ya está en uso.",
    "cc_ruc_in_use": "Este número de identificación ya está en uso.",
    "phone_numbers_in_use": "Este número de teléfono ya está en uso.",
    # Not found
    "cut_not_exist": "El corte seleccionado no existe. ({cut_code}).",
    "category_not_exist": "La categoría de material seleccionada no existe.",
    "material_not_exist": "La categoría de material seleccionada no existe.",
}


class StaticInfoErrorMessages(Enum):
    """Enum class for error messages related to static information."""

    STATUS_ERROR = {
        "code": "request_error",
        "detail": "Select a different value for the status.",
    }
    NOT_ADD_THICKNESS = {
        "code": "not_found",
        "detail": "You cannot mark a cutting technique as thickness compatible if it is not active.",
    }
    CUT_NOT_FOUND = {
        "code": "not_found",
        "detail": "The requested cutting technique was not found in the database.",
    }
    THICKNESS_NOT_FOUND = {
        "code": "not_found",
        "detail": "The thickness of the material was not found in the database.",
    }
    MATERIAL_NOT_FOUND = {
        "code": "not_found",
        "detail": "The requested material was not found in the database.",
    }
    REMOVE_CUT_COMPATIBILITY = "This action is not allowed, you cannot remove cut-off compatibilities if they are still active."
    CUT_COMPATIBILITY = (
        "This action is not allowed, you cannot add a new false cut compatibility."
    )
    ADD_REMOVE_THICKNESS = "This action is not allowed, you cannot add a new thickness to the material. This functionality is only for updating existing information."
    CHANGES_NOT_DETECTED = "No changes were detected in the thickness data. Make sure to submit information that is different from the current one."


class APIErrorMessages(Enum):
    """Enum class for error messages related to API errors."""

    USER_NOT_FOUND = {
        "code": "not_found",
        "detail": "The requested user was not found in the database.",
    }


class MethodHTTPMapped:
    """
    A class that maps HTTP methods to specific application classes, authentication
    classes, permission classes, and serializers.

    This class configures a view so that it can have different behavior based on
    the HTTP method of the request. For example, you might want to use different
    serializers for GET and POST requests, or apply different permissions for
    different methods.

    Any class that inherits from MethodHTTPMapped must also inherit from GenericAPIView.
    """

    authentication_mapping: Dict[str, Any]
    permission_mapping: Dict[str, Any]
    serializer_mapping: Dict[str, Any]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not GenericAPIView in cls.__bases__:
            raise TypeError(
                f"The {cls.__name__} class must inherit from GenericAPIView. Make sure your view definition includes GenericAPIView as a base class when using the MethodHTTPMapped class."
            )

    def get_authenticators(self) -> List[Callable]:
        """
        Returns the authenticators that the view should use for the incoming request
        based on the HTTP method.
        """

        try:
            authentication_classes = self.authentication_mapping[
                self.request.method
            ]
        except (AttributeError, KeyError):
            return [auth() for auth in self.authentication_classes]

        return [auth() for auth in authentication_classes]

    def get_permissions(self) -> List[BasePermission]:
        """
        Returns the permission classes that the view should use for the incoming
        request based on the HTTP method.
        """

        try:
            permission_classes = self.permission_mapping[self.request.method]
        except (AttributeError, KeyError):
            return [permission() for permission in self.permission_classes]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self) -> Serializer:
        """
        Returns the serializer class that the view should use for the incoming
        request based on the HTTP method.
        """

        try:
            return self.serializer_mapping[self.request.method]
        except (AttributeError, KeyError):
            return self.serializer_class


class PermissionMixin:
    """
    A class that provides permission checking functionality for views.

    This mixin class provides a method to check if the request should be permitted
    based on the permissions defined in the view.
    """

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not GenericAPIView in cls.__bases__:
            raise TypeError(
                f"The {cls.__name__} class must inherit from GenericAPIView. Make sure your view definition includes GenericAPIView as a base class when using the PermissionMixin class."
            )

    def permission_denied(
        self, request: Request, message: str = None, code: str = None
    ) -> None:
        """
        If request is not permitted, determine what kind of exception to raise.

        #### Parameters:
        - request: The incoming request object.
        - message: The message to include in the exception.
        - code: The error code to include in the exception.
        """

        if request.authenticators and not request.successful_authenticator:
            raise NotAuthenticatedAPIError()
        raise PermissionDeniedAPIError(detail=message, code=code)

    def check_permissions(self, request: Request) -> None:
        """
        Check if the request should be permitted. Raises an appropriate exception
        if the request is not permitted.

        #### Parameters:
        - request: The incoming request object.
        """

        for permission in self.get_permissions():
            if not permission.has_permission(request=request, view=self):
                self.permission_denied(
                    request=request,
                    message=getattr(permission, "message", None),
                    code=getattr(permission, "code", None),
                )


def standardize_and_replace(text: str) -> str:
    """Standardize and replace special characters in the input string."""

    def standardize_string(text: str) -> str:
        """
        NoStandardizermalize the input string by performing the following steps:
        1. Normalize the text to NFKD form (decomposes characters with accents).
        2. Remove combining characters (accents and diacritics).
        3. Remove any special characters that are not ASCII.
        """

        text = unicodedata.normalize("NFKD", text)
        text = "".join([c for c in text if not unicodedata.combining(c)])
        text = re.sub(r"[^\x00-\x7F]+", "", text)

        return text

    def replace_special_chars(text: str) -> str:
        """
        Replace special characters in the input string based on a predefined
        dictionary of replacements. The dictionary contains special characters as
        keys and their ASCII equivalents as values.
        """

        special_chars = {
            "₂": "2",
            "₃": "3",
            "₁": "1",
            " ": "_",
            ".": "",
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
        }

        for char, replacement in special_chars.items():
            text = text.replace(char, replacement)

        return text

    text = replace_special_chars(text=text)
    text = standardize_string(text=text)

    return text.lower()
