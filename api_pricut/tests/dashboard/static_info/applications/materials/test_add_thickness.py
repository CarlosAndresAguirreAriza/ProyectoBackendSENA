from apps.dashboard.infrastructure import (
    StaticInfoRepository,
    UsesCutsRepository,
)
from apps.dashboard.applications import UseCaseAddThickness
from apps.dashboard.domain.entities import (
    ThicknessMaterial,
    CuttingTechnique,
    UsesCuts,
)
from apps.exceptions import DatabaseConnectionAPIError, StaticInfoAPIError
from typing import Dict, Any
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestAddThicknessApplication:
    """
    This class encapsulates the tests for the use case or business logic
    responsible for adding a new thickness to a material.
    """

    application_class = UseCaseAddThickness

    @pytest.mark.parametrize(
        argnames="material_code, data, num_uses",
        argvalues=[
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                },
                {
                    "laser_fibra": 1,
                    "router_cnc": 1,
                    "laser_co2": 1,
                },
            ),
            (
                "triplex",
                {
                    "value": 3.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": False,
                    },
                },
                {
                    "laser_fibra": 1,
                    "router_cnc": 1,
                    "laser_co2": 0,
                },
            ),
            (
                "tol_negro",
                {
                    "value": 2.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": False,
                        "laser_co2": False,
                    },
                },
                {
                    "laser_fibra": 1,
                    "router_cnc": 0,
                    "laser_co2": 0,
                },
            ),
        ],
        ids=[
            "material_mdf",
            "material_triplex",
            "material_tol_negro",
        ],
    )
    def test_if_add_thickness(
        self,
        material_code: str,
        data: Dict[str, Any],
        num_uses: Dict[str, int],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a new thickness is added.
        """

        # Prepare the appropriate scenario in the database
        old_all_uses_cuts = UsesCuts.objects.all()
        num_thicknesses_old = ThicknessMaterial.objects.filter(
            material__code=material_code
        ).count()

        for use_instance in old_all_uses_cuts:
            use_instance.number_uses

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        thickness = use_case.add_thickness(material_code=material_code, data=data)

        # Asserting that the user has the correct data
        num_thicknesses_new = ThicknessMaterial.objects.filter(
            material__code=material_code
        ).count()

        assert num_thicknesses_new == num_thicknesses_old + 1
        assert thickness.value == data["value"]
        assert thickness.compatibility_cut == data["compatibility_cut"]

        # Asserting that the number of uses was updated correctly
        for cut_code, use in num_uses.items():
            new_uses_cut = UsesCuts.objects.get(cut__code=cut_code)

            for use_instance in old_all_uses_cuts:
                if use_instance.cut.code == cut_code:
                    old_number_uses = use_instance.number_uses
                    new_number_uses = new_uses_cut.number_uses

                    assert old_number_uses + use == new_number_uses

    @pytest.mark.parametrize(
        argnames="material_code, data",
        argvalues=[
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                },
            ),
        ],
        ids=["material_mdf"],
    )
    def test_if_reactive_cut(
        self,
        material_code: str,
        data: Dict[str, Any],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a cutting technique with 0 uses begins to be used.
        """

        # Prepare the appropriate scenario in the database
        num_thicknesses_old = ThicknessMaterial.objects.filter(
            material__code=material_code
        ).count()
        cut_uses = UsesCuts.objects.get(cut__code="laser_fibra")
        cut_uses.number_uses = 0
        cut_uses.save()

        all_thicknesses = ThicknessMaterial.objects.all()

        for thickness in all_thicknesses:
            compatibility_cut = thickness.compatibility_cut
            compatibility_cut.pop("laser_fibra")
            thickness.compatibility_cut = compatibility_cut
            thickness.save()

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        thickness = use_case.add_thickness(material_code=material_code, data=data)

        # Asserting that the correct data
        num_thicknesses_new = ThicknessMaterial.objects.filter(
            material__code=material_code
        ).count()

        assert num_thicknesses_new == num_thicknesses_old + 1
        assert use_case.modified_thicknesses is True
        assert thickness.value == data["value"]
        assert thickness.compatibility_cut == data["compatibility_cut"]

        # Asserting that the number of uses was updated correctly
        cut_uses = UsesCuts.objects.select_related("cut").get(
            cut__code="laser_fibra"
        )

        assert cut_uses.number_uses == 1

        # Asserting that the compatibility of the cutting technique was updated
        all_thicknesses = ThicknessMaterial.objects.all()

        for thickness in all_thicknesses:
            compatibility_cut = thickness.compatibility_cut

            assert compatibility_cut.get("laser_fibra", None) is not None

    @pytest.mark.parametrize(
        argnames="material_code, data",
        argvalues=[
            (
                "mdf",
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                },
            ),
        ],
        ids=["material_mdf"],
    )
    def test_if_cut_inactive(
        self,
        material_code: str,
        data: Dict[str, Any],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a cutting technique is inactive.
        """

        # Prepare the appropriate scenario in the database
        cut = CuttingTechnique.objects.get(code="laser_fibra")
        cut.is_active = False
        cut.save()

        # Instantiating the application and calling the method
        with pytest.raises(StaticInfoAPIError):
            use_case = self.application_class(
                static_info_repository=StaticInfoRepository,
                uses_cuts_repository=UsesCutsRepository,
            )
            use_case.add_thickness(material_code=material_code, data=data)

    def test_if_conection_db_failed(self) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a DatabaseConnectionAPIError exception is raised.
        """

        # Mocking the methods
        static_info_repository = Mock()
        uses_cuts_repository = Mock()
        get_material: Mock = static_info_repository.get_material
        get_material.side_effect = DatabaseConnectionAPIError
        add_thickness: Mock = static_info_repository.add_thickness
        update_thickness: Mock = static_info_repository.update_thickness
        get_use_cut: Mock = uses_cuts_repository.get
        update_use_cut: Mock = uses_cuts_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.add_thickness(material_code="meterial_code", data={})

        # Asserting that the method was not called
        update_thickness.assert_not_called()
        add_thickness.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()
