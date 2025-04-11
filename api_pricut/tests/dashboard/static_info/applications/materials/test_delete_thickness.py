from apps.dashboard.infrastructure import (
    StaticInfoRepository,
    UsesCutsRepository,
)
from apps.dashboard.applications import UseCaseDeleteThickness
from apps.dashboard.domain.entities import ThicknessMaterial, UsesCuts
from apps.exceptions import DatabaseConnectionAPIError, ResourceNotFoundAPIError
from tests.utils import empty_queryset
from typing import Dict
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestDeleteThicknessApplication:
    """
    This class encapsulates tests for the use case or business logic
    responsible for deleting a thickness from the database.
    """

    application_class = UseCaseDeleteThickness

    @pytest.mark.parametrize(
        argnames="thickness_id, num_uses",
        argvalues=[
            (
                1,
                {
                    "laser_fibra": 0,
                    "router_cnc": -1,
                    "laser_co2": -1,
                },
            ),
            (
                11,
                {
                    "laser_fibra": 0,
                    "router_cnc": -1,
                    "laser_co2": -1,
                },
            ),
        ],
        ids=[
            "material_mdf",
            "material_triplex",
        ],
    )
    def test_if_delete_thickness(
        self,
        thickness_id: int,
        num_uses: Dict[str, int],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a thickness is deleted.
        """

        # Prepare the appropriate scenario in the database
        old_all_uses_cuts = UsesCuts.objects.all()

        for use_instance in old_all_uses_cuts:
            use_instance.number_uses

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.delete_thickness(thickness_id=thickness_id)

        # Asserting that the user has the correct data
        # Asserting that the number of uses was updated correctly
        assert use_case.modified_thicknesses is False

        for cut_code, use in num_uses.items():
            new_uses_cut = UsesCuts.objects.get(cut__code=cut_code)

            for use_instance in old_all_uses_cuts:
                if use_instance.cut.code == cut_code:
                    assert (
                        use_instance.number_uses + use == new_uses_cut.number_uses
                    )

    @pytest.mark.parametrize(
        argnames="thickness_id",
        argvalues=[1],
        ids=["material_mdf"],
    )
    def test_if_desactive_cut(
        self,
        thickness_id: int,
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a cutting technique is deactivated.
        """

        # Prepare the appropriate scenario in the database
        cut_uses = UsesCuts.objects.get(cut__code="laser_co2")
        cut_uses.number_uses = 1
        cut_uses.save()

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.delete_thickness(thickness_id=thickness_id)

        # Asserting that the user has the correct data
        # Asserting that the number of uses was updated correctly
        all_thicknesses = ThicknessMaterial.objects.all()
        cut_uses = UsesCuts.objects.select_related("cut").get(
            cut__code="laser_co2"
        )

        assert use_case.modified_thicknesses is True
        assert not cut_uses.cut.is_active
        assert cut_uses.number_uses == 0

        for thickness in all_thicknesses:
            assert not thickness.compatibility_cut.get("laser_co2", False)

    def test_if_not_found_thickness(self, load_static_info) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a thickness is not found.
        """

        # Mocking the methods
        static_info_repository = Mock()
        uses_cuts_repository = Mock()
        get_thickness: Mock = static_info_repository.get_thickness
        get_thickness.return_value = empty_queryset(model=ThicknessMaterial)
        delete_thickness: Mock = static_info_repository.delete_thickness
        update_thickness: Mock = static_info_repository.update_thickness
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(ResourceNotFoundAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.delete_thickness(thickness_id=1)

        # Assert that the methods were not called
        delete_thickness.assert_not_called()
        update_thickness.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()

    def test_if_conection_db_failed(self) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a DatabaseConnectionAPIError exception is raised.
        """

        # Mocking the methods
        static_info_repository = Mock()
        uses_cuts_repository = Mock()
        get_thickness: Mock = static_info_repository.get_thickness
        get_thickness.side_effect = DatabaseConnectionAPIError
        delete_thickness: Mock = static_info_repository.delete_thickness
        update_thickness: Mock = static_info_repository.update_thickness
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.delete_thickness(thickness_id=1)

        # Assert that the methods were not called
        delete_thickness.assert_not_called()
        update_thickness.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()
