from apps.dashboard.infrastructure import StaticInfoRepository, UsesCutsRepository
from apps.dashboard.infrastructure import serializers
from apps.dashboard import applications
from apps.dashboard import swagger
from apps.authentication.jwt import JWTAuthentication
from apps.utils import MethodHTTPMapped, PermissionMixin
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework import status
import apps.permissions as permissions


class GetCreateCutAPIView(MethodHTTPMapped, PermissionMixin, GenericAPIView):
    """
    API view to retrieve and create cutting techniques.

    This view handles the retrieval of cutting techniques information via GET requests
    and the creation of new cutting techniques via POST requests. The following exceptions
    can occur during request handling and are handled by the `apps.exceptions.api_exception_handler`
    controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `ResourceNotFoundAPIError`: If the static information is not found.
    - `DatabaseConnectionAPIError`: If there is an issue connecting to the database.
    - `PermissionDeniedAPIError`: If the user does not have the required permissions and role.
    """

    authentication_mapping = {
        "GET": [],
        "POST": [JWTAuthentication],
    }
    permission_mapping = {
        "GET": [permissions.AllowAny],
        "POST": [
            permissions.IsAuthenticated,
            permissions.CanCreateCut,
            permissions.IsAdmin,
        ],
    }

    @swagger.ListCutSchema
    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle GET requests to obtain cutting techniques information.

        This method returns static information about cutting techniques. This
        information is used to provide users with a reference of the available
        options.
        """

        use_case = applications.UseCaseRetrieveCut(
            static_info_repository=StaticInfoRepository
        )
        cuts = use_case.get_cut(filters={"is_active": True})
        data_class = serializers.CutReadOnlySerializer()
        response_data = data_class.to_representation(data=cuts, many=True)

        return Response(
            data=response_data,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )

    @swagger.CreateCutSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests to create a new cutting technique.

        This method creates a new cutting technique based on the information
        provided in the request, the new cutting technique is added to the database
        and returned in the response. Only an authenticated user with the administrator
        role and the necessary permissions has access to this functionality.
        """

        serializer = serializers.CutSerializer(
            static_info_repository=StaticInfoRepository,
            data=request.data,
        )

        if not serializer.is_valid():
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseCreateCut(
            static_info_repository=StaticInfoRepository
        )
        cut = use_case.create_cut(data=serializer.validated_data)
        data_class = serializers.CutReadOnlySerializer()
        response_data = data_class.to_representation(data=cut, many=False)

        return Response(
            data=response_data,
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )


class UpdateCutBaseInfoAPIView(PermissionMixin, GenericAPIView):
    """
    API view to update cutting technique descriptions.

    The following exceptions can occur during request handling and are handled by
    the `api_pricut.apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `ResourceNotFoundAPIError`: If the static information is not found.
    - `DatabaseConnectionAPIError`: If there is an issue connecting to the database.
    - `PermissionDeniedAPIError`: If the user does not have the required permissions
    and role.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.CanUpdateCut,
        permissions.IsAdmin,
    ]

    @swagger.UpdateCutBaseInfo
    def patch(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle PATCH requests to update cutting technique base info.

        This method updates an existing cutting technique based on the information
        provided in the request, the updated cutting technique is returned in the
        response. Only an authenticated user with the administrator role and the necessary
        permissions has access to this functionality.
        """

        serializer = serializers.CutBaseInfoSerializer(
            static_info_repository=StaticInfoRepository,
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseUpdateCut(
            static_info_repository=StaticInfoRepository
        )
        cut = use_case.update_cut_baseinfo(
            data=serializer.validated_data,
            cut_code=kwargs["cut_code"],
        )
        data_class = serializers.CutBaseInfoReadOnlySerializer()
        response_data = data_class.to_representation(instance=cut)

        return Response(
            data=response_data,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )


class UpdateCutDescriptionAPIView(PermissionMixin, GenericAPIView):
    """
    API view to update cutting technique descriptions.

    The following exceptions can occur during request handling and are handled by
    the `api_pricut.apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `ResourceNotFoundAPIError`: If the static information is not found.
    - `DatabaseConnectionAPIError`: If there is an issue connecting to the database.
    - `PermissionDeniedAPIError`: If the user does not have the required permissions
    and role.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.CanUpdateCut,
        permissions.IsAdmin,
    ]

    @swagger.UpdateCutDescription
    def patch(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle PATCH requests to update cutting technique descriptions.

        This method updates an existing cutting technique based on the information
        provided in the request, the updated cutting technique is returned in the
        response. Only an authenticated user with the administrator role and the necessary
        permissions has access to this functionality.
        """

        serializer = serializers.CutDescriptionSerializer(
            data=request.data,
            partial=True,
        )

        if not serializer.is_valid():
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseUpdateCut(
            static_info_repository=StaticInfoRepository
        )
        cut = use_case.update_cut_descriptions(
            data=serializer.validated_data,
            cut_code=kwargs["cut_code"],
        )
        data_class = serializers.CutDescriptionReadOnlySerializer()
        response_data = data_class.to_representation(instance=cut)

        return Response(
            data=response_data,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )


class CutStatusAPIView(PermissionMixin, GenericAPIView):
    """
    API view to change the status of cutting techniques.

    The following exceptions can occur during request handling and are handled by the
    `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `ResourceNotFoundAPIError`: If the cutting technique not found in the database.
    - `DatabaseConnectionAPIError`: If there is an issue connecting to the database.
    - StaticInfoAPIError: If the cutting technique is already in the desired state.
    - `PermissionDeniedAPIError`: If the user does not have the required permissions
    and role.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdmin,
        permissions.CanChangeStatusCut,
    ]

    @swagger.CutStatusSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests to change the status of a cutting technique.

        This method changes the state of a cutting technique depending on the function,
        this state allows to control if the information of a cutting technique can be
        displayed to the end user. Only an authenticated user with the administrator
        role and the necessary permissions has access to this functionality.
        """

        serializer = serializers.StatusSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                data={
                    "code": "invalid_request_data",
                    "detail": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
                content_type="application/json",
            )

        use_case = applications.UseCaseChangeCutStatus(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.change_cut_status(
            new_status=serializer.validated_data["status"],
            cut_code=kwargs["cut_code"],
        )

        return Response(
            data={"modified_thicknesses": use_case.modified_thicknesses},
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
