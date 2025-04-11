from apps.users.infrastructure import views
from django.urls import path


urlpatterns = [
    path(
        route="natural_person/",
        view=views.NaturalPersonCreateAPIView.as_view(),
        name="create_natural_person",
    ),
    path(
        route="natural_person/<str:user_uuid>/",
        view=views.NaturalPersonGetAPIView.as_view(),
        name="get_natural_person",
    ),
    path(
        route="company/",
        view=views.CompanyCreateAPIView.as_view(),
        name="create_company",
    ),
]
