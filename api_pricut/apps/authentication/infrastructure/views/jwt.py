from apps.authentication.infrastructure import serializers
from apps.authentication import swagger, applications
from apps.authentication.jwt import JWTAuthentication
from apps.users.infrastructure import UserRepository
from apps.utils import PermissionMixin
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
import apps.permissions as permissions


class JWTLoginAPIView(TokenObtainPairView):
    """
    API view for user authentication.

    The following exceptions can occur during request handling and are
    handled by the `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `DatabaseConnectionAPIError`: If there is an operational error with the \
    database.
    - `PermissionDeniedAPIError`: If the user does not have the necessary
    permissions.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger.JWTLoginSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests for user authentication.

        This method allows for the authentication of a user, it expects a POST
        request with their credentials. Successful authentication will result in the
        creation of the user access token if their credentials are valid, their
        account is active, and they have the necessary permissions to perform this
        action.
        """

        serializer = serializers.JWTLoginSerializer(data=request.data)

        if serializer.is_valid() is False:
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseCreateToken
        access_token = use_case.validate_credentials(
            credentials=serializer.validated_data
        )

        return Response(
            data={"access_token": access_token},
            status=status.HTTP_200_OK,
            content_type="application/json",
        )


class JWTUpdateAPIView(PermissionMixin, GenericAPIView):
    """
    API view for updating user tokens.

    The following exceptions can occur during request handling and are
    handled by the `apps.exceptions.api_exception_handler` controller:

    - `ResourceNotFoundAPIError`: If the user does not exist.
    - `JWTAPIError`: If there is an issue with the JSON Web Token.
    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger.JWTUpdateSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests for token refresh.

        This method allows updating the JSON Web Tokens of an authenticated user,
        waiting for a POST request with the access and update tokens. A successful
        refresh will consist of creating new access token to keep the user
        authenticated and invalidating the previous refresh token by adding it to
        the blacklist.
        """

        serializer = serializers.JWTUpdateSerializer(data=request.data)

        if serializer.is_valid() is False:
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseRefreshToken(user_repository=UserRepository)
        new_access_token = use_case.refresh_token(
            access_token=serializer.validated_data["access_token"]
        )

        return Response(
            data={"access_token": new_access_token},
            status=status.HTTP_200_OK,
            content_type="application/json",
        )


class JWTLogoutAPIView(PermissionMixin, GenericAPIView):
    """
    View to manage user logout.

    This view handles POST requests to log out a JWT authenticated user. The
    following exceptions can occur during request handling and are handled by the
    `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `ResourceNotFoundAPIError`: If user or token is not found.
    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @swagger.JWTLogoutSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handles POST requests for user logout.

        This method allows to logout an authenticated user. Wait for a POST request
        with the update token. A successful logout will consist of invalidating the
        access token by adding them to the blacklist.
        """

        use_case = applications.UseCaseInvalidateToken
        use_case.invalidate_token(access_token=request.auth)

        return Response(
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
