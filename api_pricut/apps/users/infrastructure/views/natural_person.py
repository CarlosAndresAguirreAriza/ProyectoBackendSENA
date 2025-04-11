from apps.users.infrastructure import UserRepository
from apps.users.infrastructure import serializers
from apps.users import swagger, applications
from apps.authentication.jwt import JWTAuthentication
from apps.utils import MethodHTTPMapped, PermissionMixin
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework import status
import apps.permissions as permissions


class NaturalPersonCreateAPIView(PermissionMixin, GenericAPIView):
    """
    API view for creating a new user with the `natural person` role.

    The following exceptions can occur during request handling and are handled by
    the `apps.exceptions.api_exception_handler` controller:

    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger.CreateNaturalPersonSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests for natural person user registration.

        This method allows you to register a new user with the 'natural person'
        role, waiting for a POST request with the registration data. A successful
        registration will consist of saving the user's information in the database
        and assigning the permissions for their role.
        """

        serializer = serializers.RegisterNaturalPersonSerializer(
            user_repository=UserRepository,
            data=request.data,
        )

        if serializer.is_valid() is False:
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseRegisterUser(user_repository=UserRepository)
        use_case.create_natural_person(data=serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class NaturalPersonGetAPIView(MethodHTTPMapped, PermissionMixin, GenericAPIView):
    """
    API view for retrieving user information with the `natural perso` role.

    It uses a mapping approach to determine the appropriate application logic
    and permissions based on the HTTP method of the incoming request. The
    following exceptions can occur during request handling and are handled by
    the `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `ResourceNotFoundAPIError`: If the user is not found in the database.
    - `PermissionDeniedAPIError`: If the user does not have the required \
    permissions and role.
    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    """

    authentication_mapping = {"GET": [JWTAuthentication]}
    permission_mapping = {
        "GET": [
            permissions.IsAuthenticated,
            permissions.IsAccessTokenOwner,
            permissions.IsNaturalPerson,
            permissions.CanReadUserData,
        ],
    }

    @swagger.RetrieveNaturalPersonSchema
    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle GET requests to obtain user information.

        This method returns the information for the user account with the
        'naturalperson' role associated with the request's access token, without
        exposing sensitive data. The information is only provided if the user has
        permission to read their own data and has the 'naturalperson' role.
        """

        use_case = applications.UseCaseRetrieveUser(user_repository=UserRepository)
        user = use_case.get_natural_person(user_uuid=kwargs["user_uuid"])
        data_class = serializers.NaturalPersonReadOnlySerializer()
        response_data = data_class.to_representation(instance=user)

        return Response(
            data=response_data,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
