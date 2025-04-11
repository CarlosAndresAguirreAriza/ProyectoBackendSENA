from apps.dashboard.infrastructure import (
    StaticInfoRepository,
    UsesCutsRepository,
)
from apps.dashboard.applications import UseCaseChangeMaterialStatus
from apps.dashboard.domain.entities import Material, ThicknessMaterial, UsesCuts
from apps.exceptions import (
    DatabaseConnectionAPIError,
    ResourceNotFoundAPIError,
    StaticInfoAPIError,
)
from tests.utils import empty_queryset
from unittest.mock import Mock
from typing import Dict
import pytest


@pytest.mark.django_db
class TestChangeMaterialStatusApplication:
    """
    This class encapsulates tests for the use case responsible for changing the
    status of a material in the database.
    """

    application_class = UseCaseChangeMaterialStatus

    @pytest.mark.parametrize(
        argnames="material_code, new_status, num_uses",
        argvalues=[
            (
                "mdf",
                True,
                {
                    "laser_fibra": 0,
                    "router_cnc": 10,
                    "laser_co2": 4,
                },
            ),
            (
                "mdf",
                False,
                {
                    "laser_fibra": 0,
                    "router_cnc": -10,
                    "laser_co2": -4,
                },
            ),
        ],
        ids=[
            "change_status_to_active",
            "change_status_to_inactive",
        ],
    )
    def test_if_change_material_status(
        self,
        material_code: str,
        new_status: bool,
        num_uses: Dict[str, int],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a material in the database.
        """

        # Prepare the appropriate scenario in the database
        material_status = not new_status
        old_all_uses_cuts = UsesCuts.objects.select_related("cut").all()
        material = Material.objects.filter(code=material_code).first()
        material.is_active = material_status
        material.save()

        # Updating the number of uses for each cut
        for use_instance in old_all_uses_cuts:
            num_uses_cut = num_uses[use_instance.cut.code]
            uses_cut = use_instance.number_uses

            if material_status:
                uses_cut += abs(num_uses_cut)
            else:
                uses_cut -= abs(num_uses_cut)

            use_instance.save()

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.change_material_status(
            material_code=material_code,
            new_status=new_status,
        )

        # Asserting that if the thicknesses were modified
        assert use_case.modified_thicknesses is False

        # Asserting that the number of uses was updated correctly
        for cut_code, use in num_uses.items():
            new_uses_cut = UsesCuts.objects.get(cut__code=cut_code)

            for use_instance in old_all_uses_cuts:
                if use_instance.cut.code == cut_code:
                    old_number_uses = use_instance.number_uses
                    new_number_uses = new_uses_cut.number_uses

                    assert old_number_uses + use == new_number_uses

    @pytest.mark.parametrize(
        argnames="material_code, new_status, num_uses",
        argvalues=[
            (
                "mdf",
                False,
                {
                    "laser_fibra": 0,
                    "router_cnc": -10,
                    "laser_co2": -4,
                },
            ),
        ],
        ids=["desactive_cut"],
    )
    def test_if_desactive_cut(
        self,
        material_code: str,
        new_status: bool,
        num_uses: Dict[str, int],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a material in the database
        when the cut is inactive.
        """

        # Prepare the appropriate scenario in the database
        cut_uses = (
            UsesCuts.objects.select_related("cut")
            .filter(cut__code="router_cnc")
            .first()
        )
        cut_uses.number_uses = 10
        cut_uses.save()

        old_all_uses_cuts = UsesCuts.objects.all()

        for use_instance in old_all_uses_cuts:
            use_instance.number_uses

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        use_case.change_material_status(
            material_code=material_code,
            new_status=new_status,
        )

        # Asserting that if the thicknesses were modified
        assert use_case.modified_thicknesses is True

        # Asserting that the cut is active
        cut_uses = (
            UsesCuts.objects.select_related("cut")
            .filter(cut__code="router_cnc")
            .first()
        )

        assert cut_uses.cut.is_active is False

        # Asserting that the number of uses was updated correctly
        for cut_code, use in num_uses.items():
            new_uses_cut = UsesCuts.objects.get(cut__code=cut_code)

            for use_instance in old_all_uses_cuts:
                if use_instance.cut.code == cut_code:
                    old_number_uses = use_instance.number_uses
                    new_number_uses = new_uses_cut.number_uses

                    assert old_number_uses + use == new_number_uses

        # Asserting that the compatibility_cut was updated correctly
        all_thicknesses = ThicknessMaterial.objects.all()

        for thickness in all_thicknesses:
            compatibility_cut = thickness.compatibility_cut

            assert compatibility_cut.get("router_cnc", None) is None

    @pytest.mark.parametrize(
        argnames="material_code, new_status",
        argvalues=[
            ("mdf", True),
            ("mdf", False),
        ],
        ids=[
            "change_status_to_active",
            "change_status_to_inactive",
        ],
    )
    def test_if_status_error(
        self,
        material_code: str,
        new_status: bool,
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a material in the database
        when the status is the same as the new status.
        """

        # Prepare the appropriate scenario in the database
        query_set = Material.objects.filter(code=material_code)
        material = query_set.first()
        material.is_active = new_status
        material.save()

        # Mocking the methods
        static_info_repository = Mock()
        uses_cuts_repository = Mock()
        get_material: Mock = static_info_repository.get_material
        get_material.return_value = query_set
        change_status: Mock = static_info_repository.change_status
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(StaticInfoAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.change_material_status(
                material_code=material_code,
                new_status=new_status,
            )

        # Assert that the methods were not called
        change_status.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()

    def test_if_not_found_material(self, load_static_info) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a material in the database
        when the material is not found.
        """

        # Mocking the methods
        static_info_repository = Mock()
        uses_cuts_repository = Mock()
        get_material: Mock = static_info_repository.get_material
        get_material.return_value = empty_queryset(model=Material)
        change_status: Mock = static_info_repository.change_status
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(ResourceNotFoundAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.change_material_status(
                material_code="material_code",
                new_status=True,
            )

        # Assert that the methods were not called
        change_status.assert_not_called()
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
        get_material: Mock = static_info_repository.get_material
        get_material.side_effect = DatabaseConnectionAPIError
        change_status: Mock = static_info_repository.change_status
        get_use_cut: Mock = static_info_repository.get
        update_use_cut: Mock = static_info_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.change_material_status(
                material_code="material_code",
                new_status=True,
            )

        # Assert that the methods were not called
        change_status.assert_not_called()
        get_use_cut.assert_not_called()
        update_use_cut.assert_not_called()
