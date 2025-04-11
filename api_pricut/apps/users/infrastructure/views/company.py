from apps.users.infrastructure import UserRepository
from apps.users.infrastructure import serializers
from apps.users import swagger, applications
from apps.utils import PermissionMixin
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework import status
import apps.permissions as permissions


class CompanyCreateAPIView(PermissionMixin, GenericAPIView):
    """
    API view for creating a new user with the `company` role.

    The following exceptions can occur during request handling and are handled by
    the `apps.exceptions.api_exception_handler` controller:

    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    """

    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger.CreateCompanySchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests for company user registration.

        This method allows you to register a new company user, waiting for a POST
        request with the registration data. A successful registration will consist
        of saving the user's information in the database and configuring the
        permissions for their role.
        """

        serializer = serializers.RegisterCompanySerializer(
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
        use_case.create_company(data=serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)
