from apps.dashboard.infrastructure import (
    StaticInfoRepository,
    UsesCutsRepository,
)
from apps.dashboard.applications import UseCaseUpdateThickness
from apps.dashboard.domain.entities import (
    ThicknessMaterial,
    CuttingTechnique,
    UsesCuts,
)
from apps.exceptions import (
    DatabaseConnectionAPIError,
    ResourceNotFoundAPIError,
    StaticInfoAPIError,
)
from tests.utils import empty_queryset
from typing import Dict, Any
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestUpdateThicknessApplication:
    """
    This class encapsulates tests for the use case or business logic
    responsible for updating a thickness to a material.
    """

    application_class = UseCaseUpdateThickness

    @pytest.mark.parametrize(
        argnames="thickness_id, data, num_uses",
        argvalues=[
            (
                1,
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
                    "router_cnc": 0,
                    "laser_co2": 0,
                },
            ),
            (
                11,
                {
                    "value": 3.50,
                    "compatibility_cut": {
                        "laser_fibra": True,
                        "router_cnc": False,
                        "laser_co2": False,
                    },
                },
                {
                    "laser_fibra": 1,
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
    def test_if_update_thickness(
        self,
        thickness_id: int,
        data: Dict[str, Any],
        num_uses: Dict[str, int],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a thickness is updated.
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
        thickness = use_case.update_thickness(
            thickness_id=thickness_id,
            data=data,
        )

        # Asserting that the user has the correct data
        assert use_case.modified_thicknesses is False
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
        argnames="thickness_id, data",
        argvalues=[
            (
                1,
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
        thickness_id: int,
        data: Dict[str, Any],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a cutting technique with 0 uses begins to be used.
        """

        # Prepare the appropriate scenario in the database
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
        thickness = use_case.update_thickness(
            thickness_id=thickness_id,
            data=data,
        )

        # Asserting that the correct data
        cut_uses = UsesCuts.objects.select_related("cut").get(
            cut__code="laser_fibra"
        )

        assert use_case.modified_thicknesses is True
        assert thickness.value == data["value"]
        assert thickness.compatibility_cut == data["compatibility_cut"]
        assert cut_uses.number_uses == 1

        all_thicknesses = ThicknessMaterial.objects.all()

        for thickness in all_thicknesses:
            compatibility_cut = thickness.compatibility_cut

            assert compatibility_cut.get("laser_fibra", None) is not None

    @pytest.mark.parametrize(
        argnames="thickness_id, data",
        argvalues=[
            (
                1,
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": False,
                        "router_cnc": True,
                        "laser_co2": False,
                    },
                },
            ),
        ],
        ids=["material_mdf"],
    )
    def test_if_desactive_cut(
        self,
        thickness_id: int,
        data: Dict[str, Any],
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
        thickness = use_case.update_thickness(
            thickness_id=thickness_id,
            data=data,
        )

        # Asserting that the correct data
        all_thicknesses = ThicknessMaterial.objects.all()
        cut_uses = UsesCuts.objects.select_related("cut").get(
            cut__code="laser_co2"
        )

        assert use_case.modified_thicknesses is True
        assert thickness.value == data["value"]
        assert thickness.compatibility_cut == data["compatibility_cut"]
        assert not cut_uses.cut.is_active
        assert cut_uses.number_uses == 0

        for thickness in all_thicknesses:
            assert not thickness.compatibility_cut.get("laser_co2", False)

    @pytest.mark.parametrize(
        argnames="thickness_id, data",
        argvalues=[
            (
                1,
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
        thickness_id: int,
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
            use_case.update_thickness(thickness_id=thickness_id, data=data)

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
        update_thickness: Mock = static_info_repository.update_thickness
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(ResourceNotFoundAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.update_thickness(thickness_id=1, data={})

        # Assert that the methods were not called
        update_thickness.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()

    @pytest.mark.parametrize(
        argnames="thickness_id, data",
        argvalues=[
            (
                1,
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": False,
                        "router_cnc": True,
                        "laser_co2": True,
                    },
                },
            ),
            (
                1,
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": False,
                        "router_cnc": False,
                    },
                },
            ),
            (
                1,
                {
                    "value": 5.50,
                    "compatibility_cut": {
                        "laser_fibra": False,
                        "router_cnc": False,
                        "laser_co2": True,
                        "other_cut": False,
                    },
                },
            ),
        ],
        ids=[
            "changes_not_detected",
            "remove_cut_compatibility",
            "add_cut_compatibility_in_false",
        ],
    )
    def test_if_data_cut_compatibility_section_invalid(
        self,
        thickness_id: int,
        data: Dict[str, Any],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when the data is invalid.
        """

        # Instantiating the application and calling the method
        with pytest.raises(StaticInfoAPIError):
            use_case = self.application_class(
                static_info_repository=StaticInfoRepository,
                uses_cuts_repository=UsesCutsRepository,
            )
            use_case.update_thickness(
                thickness_id=thickness_id,
                data=data,
            )

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
        update_thickness: Mock = static_info_repository.update_thickness
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.update_thickness(thickness_id=1, data={})

        # Assert that the methods were not called
        update_thickness.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()
