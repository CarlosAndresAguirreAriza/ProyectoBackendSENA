from apps.users.domain.constants import (
    NATURAL_PERSON_ROLE,
    USER_PERMISSIONS,
    COMPANY_ROLE,
    ADMIN_ROLE,
)
from apps.authentication.domain.constants import AUTH_PERMISSIONS
from apps.dashboard.domain.constants import STATIC_INFO_PERMISSIONS
from rest_framework.permissions import BasePermission, AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView


PERMISSIONS = {**AUTH_PERMISSIONS, **STATIC_INFO_PERMISSIONS, **USER_PERMISSIONS}

USER_ROLE_PERMISSIONS = {
    NATURAL_PERSON_ROLE: [
        "view_base_data",
        "change_base_data",
        "delete_base_data",
        "view_naturalperson",
        "change_naturalperson",
        "delete_naturalperson",
        "jwt_auth",
    ],
    COMPANY_ROLE: [
        "view_base_data",
        "change_base_data",
        "delete_base_data",
        "view_company",
        "change_company",
        "delete_company",
        "jwt_auth",
    ],
    ADMIN_ROLE: [
        "add_cuttingtechnique",
        "view_cuttingtechnique",
        "change_cuttingtechnique",
        "activate_cuttingtechnique",
        "deactivate_cuttingtechnique",
        "delete_cuttingtechnique",
        "add_material",
        "view_material",
        "change_material",
        "activate_material",
        "deactivate_material",
        "delete_material",
        "add_thickness",
        "change_thickness",
        "delete_thickness",
        "view_base_data",
        "view_admin",
        "jwt_auth",
    ],
}


# User permissions
class IsNaturalPerson(BasePermission):
    """Permission class that checks if the user has the natural person role."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.role == NATURAL_PERSON_ROLE


class IsAdmin(BasePermission):
    """Permission class that checks if the user has the admin role."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.role == ADMIN_ROLE


class IsAccessTokenOwner(BasePermission):
    """Permission class that checks if the user is the owner of the access token."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return view.kwargs["user_uuid"] == request.auth.payload["user_uuid"]


class CanReadUserData(BasePermission):
    """Permission class that checks if the user can read user data."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        permissions_read = {
            NATURAL_PERSON_ROLE: PERMISSIONS["view_naturalperson"],
            ADMIN_ROLE: PERMISSIONS["view_admin"],
            COMPANY_ROLE: PERMISSIONS["view_company"],
        }
        perm_list = [
            PERMISSIONS["view_base_data"],
            permissions_read[request.user.role],
        ]

        return request.user.has_perms(perm_list=perm_list)


# Satic info permissions
class CanCreateCut(BasePermission):
    """Permission class that checks if the user can create cutting technique."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.has_perm(perm=PERMISSIONS["add_cuttingtechnique"])


class CanUpdateCut(BasePermission):
    """Permission class that checks if the user can update cutting technique."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.has_perm(perm=PERMISSIONS["change_cuttingtechnique"])


class CanChangeStatusCut(BasePermission):
    """Permission class that checks if the user can change the status of cutting technique."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:
        perm_list = [
            PERMISSIONS["activate_cuttingtechnique"],
            PERMISSIONS["deactivate_cuttingtechnique"],
        ]

        return request.user.has_perms(perm_list=perm_list)


class CanUpdateMaterial(BasePermission):
    """Permission class that checks if the user can update material."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.has_perm(perm=PERMISSIONS["change_material"])


class CanChangeStatusMaterial(BasePermission):
    """Permission class that checks if the user can change the status of material."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:
        perm_list = [
            PERMISSIONS["activate_material"],
            PERMISSIONS["deactivate_material"],
        ]

        return request.user.has_perms(perm_list=perm_list)


class CanAddThickness(BasePermission):
    """Permission class that checks if the user can add thickness."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.has_perm(perm=PERMISSIONS["add_thickness"])


class CanUpdateThickness(BasePermission):
    """Permission class that checks if the user can update thickness."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.has_perm(perm=PERMISSIONS["change_thickness"])


class CanDeleteThickness(BasePermission):
    """Permission class that checks if the user can delete thickness."""

    def has_permission(self, request: Request, view: GenericAPIView) -> bool:

        return request.user.has_perm(perm=PERMISSIONS["delete_thickness"])
