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


class MaterialListAPIView(MethodHTTPMapped, PermissionMixin, GenericAPIView):
    """
    API view to list materials.

    This view uses a mapping approach to determine the appropriate application
    logic, permissions, and serializers based on the HTTP method of the incoming
    request. The following exceptions can occur during request handling and are
    handled by the `apps.exceptions.api_exception_handler` controller:

    - ResourceNotFoundAPIError: If the material is not found.
    - DatabaseConnectionAPIError: If there is an issue connecting to the database.
    """

    authentication_mapping = {
        "GET": [],
    }
    permission_mapping = {
        "GET": [permissions.AllowAny],
    }

    @swagger.ListMaterialSchema
    def get(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle GET requests to obtain information about all materials.

        This method returns static information about materials, including available
        thicknesses and their compatibility with different cutting techniques
        respectively. This information is used to provide users with a reference of
        the available options.
        """

        use_case = applications.UseCaseRetrieveMaterial(
            static_info_repository=StaticInfoRepository
        )
        materials = use_case.get_material(filters={"is_active": True})
        data_class = serializers.MaterialReadOnlySerializer()
        response_data = data_class.to_representation(data=materials, many=True)

        return Response(
            data=response_data,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )


class MaterialStatusAPIView(PermissionMixin, GenericAPIView):
    """
    API view to change the status of a material.

    The following exceptions can occur during request handling and are
    handled by the `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `PermissionDeniedAPIError`: If the user does not have the required permissions
    and role.
    - `ResourceNotFoundAPIError`: If the material is not found.
    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    - `StaticInfoAPIError:` If you attempt to make a modification to the material
    information that is not permitted.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdmin,
        permissions.CanChangeStatusMaterial,
    ]

    @swagger.MaterialStatusSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests to change the status of a material.

        This method changes the status of a material in the database. The new status
        is provided in the request body, and only an authenticated user with the
        administrator role and the necessary permissions has access to this functionality.
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

        use_case = applications.UseCaseChangeMaterialStatus(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.change_material_status(
            material_code=kwargs["material_code"],
            new_status=serializer.validated_data["status"],
        )

        return Response(
            data={"modified_thicknesses": use_case.modified_thicknesses},
            status=status.HTTP_200_OK,
            content_type="application/json",
        )


class ThicknessCreateAPIView(PermissionMixin, GenericAPIView):
    """
    API view to add a new thickness to a material.

    The following exceptions can occur during request handling and are
    handled by the `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `PermissionDeniedAPIError`: If the user does not have the required permissions
    and role.
    - `ResourceNotFoundAPIError`: The material to which the thickness is to be added
    was not found in the database.
    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    - `StaticInfoAPIError:` If you attempt to make a modification to the material
    information that is not permitted.
    """

    authentication_classes = [JWTAuthentication]
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdmin,
        permissions.CanAddThickness,
    ]

    @swagger.CreateThicknessSchema
    def post(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle POST requests to add a new thickness to a material.

        This method adds a new thickness to a material in the database. The thickness
        information is provided in the request body, and only an authenticated user with
        the administrator role and the necessary permissions has access to this functionality.
        """

        serializer = serializers.CreateThicknessSerializer(
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

        use_case = applications.UseCaseAddThickness(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        thickness = use_case.add_thickness(
            material_code=kwargs["material_code"],
            data=serializer.validated_data,
        )
        data_class = serializers.ThicknessReadOnlySerializer()
        response_data = {
            "modified_thicknesses": use_case.modified_thicknesses,
            "data": data_class.to_representation(data=thickness, many=False),
        }

        return Response(
            data=response_data,
            status=status.HTTP_201_CREATED,
            content_type="application/json",
        )


class ThicknessDeleteUpdateAPIView(
    MethodHTTPMapped,
    PermissionMixin,
    GenericAPIView,
):
    """
    API view to manage thicknesses of materials.

    The following exceptions can occur during request handling and are handled
    by the `apps.exceptions.api_exception_handler` controller:

    - `JWTError`: If there is an issue with the JSON Web Token.
    - `AuthenticationFailedAPIError`: If the user authentication fails.
    - `ResourceNotFoundAPIError`: If the thickness is not found.
    - `PermissionDeniedAPIError`: If the user does not have the required
    permissions and role.
    - `DatabaseConnectionAPIError`: If there is an operational error with the
    database.
    """

    authentication_mapping = {
        "PATCH": [JWTAuthentication],
        "DELETE": [JWTAuthentication],
    }
    permission_mapping = {
        "PATCH": [
            permissions.IsAuthenticated,
            permissions.IsAdmin,
            permissions.CanUpdateThickness,
        ],
        "DELETE": [
            permissions.IsAuthenticated,
            permissions.IsAdmin,
            permissions.CanDeleteThickness,
        ],
    }

    @swagger.UpdateThicknessSchema
    def patch(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle PATCH requests to update material thickness information.

        This method adds or updates a material thickness to the database. Thickness information
        is provided in the request body and only an authenticated user with the administrator
        role and the necessary permissions has access to this functionality.
        """

        serializer = serializers.UpdateThicknessSerializer(
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

        use_case = applications.UseCaseUpdateThickness(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        thickness = use_case.update_thickness(
            thickness_id=kwargs["thickness_id"],
            data=serializer.validated_data,
        )
        data_class = serializers.ThicknessReadOnlySerializer()
        response_data = {
            "modified_thicknesses": use_case.modified_thicknesses,
            "data": data_class.to_representation(data=thickness, many=False),
        }

        return Response(
            data=response_data,
            status=status.HTTP_200_OK,
            content_type="application/json",
        )

    @swagger.DeleteThicknessSchema
    def delete(self, request: Request, *args, **kwargs) -> Response:
        """
        Handle DELETE requests to remove a thickness from a material.

        This method removes a thickness from a material in the database. The thickness
        information is provided in the request body, and only an authenticated user with
        the administrator role and the necessary permissions has access to this functionality
        to remove a thickness.
        """

        use_case = applications.UseCaseDeleteThickness(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.delete_thickness(thickness_id=kwargs["thickness_id"])

        return Response(
            data={"modified_thicknesses": use_case.modified_thicknesses},
            status=status.HTTP_200_OK,
            content_type="application/json",
        )
