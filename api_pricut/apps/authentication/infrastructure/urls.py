from apps.authentication.infrastructure import views
from django.urls import path


urlpatterns = [
    path(
        route="jwt/login/",
        view=views.JWTLoginAPIView.as_view(),
        name="jwt_login",
    ),
    path(
        route="jwt/update/",
        view=views.JWTUpdateAPIView.as_view(),
        name="jwt_update",
    ),
    path(
        route="jwt/logout/",
        view=views.JWTLogoutAPIView.as_view(),
        name="jwt_logout",
    ),
]
