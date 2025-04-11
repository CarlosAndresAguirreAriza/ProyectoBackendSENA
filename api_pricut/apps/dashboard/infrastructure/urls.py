from apps.dashboard.infrastructure import views
from django.urls import path


urlpatterns = [
    path(
        route="static_info/materials/",
        view=views.MaterialListAPIView.as_view(),
        name="list_material",
    ),
    path(
        route="static_info/materials/<str:material_code>/change_status/",
        view=views.MaterialStatusAPIView.as_view(),
        name="change_material_status",
    ),
    path(
        route="static_info/materials/<str:material_code>/thickness/",
        view=views.ThicknessCreateAPIView.as_view(),
        name="create_thickness",
    ),
    path(
        route="static_info/materials/thickness/<int:thickness_id>/",
        view=views.ThicknessDeleteUpdateAPIView.as_view(),
        name="delete_update_thickness",
    ),
    path(
        route="static_info/cuts/",
        view=views.GetCreateCutAPIView.as_view(),
        name="get_create_cut",
    ),
    path(
        route="static_info/cuts/<str:cut_code>/base_info/",
        view=views.UpdateCutBaseInfoAPIView.as_view(),
        name="update_cut_base_info",
    ),
    path(
        route="static_info/cuts/<str:cut_code>/descriptions/",
        view=views.UpdateCutDescriptionAPIView.as_view(),
        name="update_cut_descriptions",
    ),
    path(
        route="static_info/cuts/<str:cut_code>/change_status/",
        view=views.CutStatusAPIView.as_view(),
        name="change_cut_status",
    ),
]
