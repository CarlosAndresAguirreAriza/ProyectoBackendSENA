from apps.dashboard.infrastructure import StaticInfoRepository
from apps.dashboard.applications import UseCaseRetrieveMaterial
from apps.dashboard.domain.entities import Material
from apps.exceptions import (
    DatabaseConnectionAPIError,
    ResourceNotFoundAPIError,
)
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestRetrieveMaterialApplication:
    """
    This class encapsulates all tests for the use case responsible for retrieving
    material data from the database.
    """

    application_class = UseCaseRetrieveMaterial

    @pytest.mark.parametrize(
        argnames="is_active",
        argvalues=[True, False],
        ids=["active", "inactive"],
    )
    def test_if_get_material(self, is_active: bool, load_static_info) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when retrieving a material.
        """

        # Prepare the appropriate scenario in the database
        matrerial = Material.objects.filter(is_active=True).first()
        matrerial.is_active = is_active
        matrerial.save()

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
        )
        materials = use_case.get_material(filters={"is_active": is_active})

        # Asserting that the correct data
        num_materials = Material.objects.filter(is_active=is_active).count()

        assert materials.count() == num_materials

    def test_if_not_found_material(self, load_static_info) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a material is not found.
        """

        # Instantiating the application and calling the method
        with pytest.raises(ResourceNotFoundAPIError):
            use_case = self.application_class(
                static_info_repository=StaticInfoRepository,
            )
            use_case.get_material(filters={"code": "code"})

    def test_if_conection_db_failed(self) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a DatabaseConnectionAPIError exception is raised.
        """

        # Mocking the methods
        static_info_repository = Mock()
        get_material: Mock = static_info_repository.get_material
        get_material.side_effect = DatabaseConnectionAPIError

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
            )
            use_case.get_material(filters={"code": "code"})
