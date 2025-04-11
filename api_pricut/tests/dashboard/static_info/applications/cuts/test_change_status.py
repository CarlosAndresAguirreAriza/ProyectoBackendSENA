from apps.dashboard.infrastructure import StaticInfoRepository, UsesCutsRepository
from apps.dashboard.applications import UseCaseChangeCutStatus
from apps.dashboard.domain.entities import ThicknessMaterial, CuttingTechnique
from apps.exceptions import (
    DatabaseConnectionAPIError,
    ResourceNotFoundAPIError,
    StaticInfoAPIError,
)
from tests.utils import empty_queryset
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestChangeCutStatusApplication:
    """
    This class encapsulates tests for the use case responsible for changing the
    status of a cutting technique in the database.
    """

    application_class = UseCaseChangeCutStatus

    @pytest.mark.parametrize(
        argnames="cut_code, new_status",
        argvalues=[
            ("router_cnc", True),
            ("laser_fibra", False),
        ],
        ids=[
            "change_status_to_active",
            "change_status_to_inactive",
        ],
    )
    def test_if_change_cut_status(
        self,
        cut_code: str,
        new_status: bool,
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a cutting technique in
        the database.
        """

        # Prepare the appropriate scenario in the database
        cut_status = not new_status
        cut = CuttingTechnique.objects.filter(code=cut_code).first()
        cut.is_active = cut_status
        cut.save()

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository,
            uses_cuts_repository=UsesCutsRepository,
        )
        cut = use_case.change_cut_status(cut_code=cut_code, new_status=new_status)

        # Asserting that response data is correct
        cut = CuttingTechnique.objects.filter(code=cut_code).first()

        assert cut.is_active == new_status

        # Asserting that the compatibility_cut was updated correctly
        if new_status is False:
            all_thicknesses = ThicknessMaterial.objects.all()

            for thickness in all_thicknesses:
                compatibility_cut = thickness.compatibility_cut

                assert compatibility_cut.get(cut_code, None) is None

    @pytest.mark.parametrize(
        argnames="cut_code, new_status",
        argvalues=[("other_cut", True)],
        ids=["cut_not_found"],
    )
    def test_if_not_found_cut(
        self,
        cut_code: str,
        new_status: bool,
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a cutting technique in
        the database when the cutting technique is not found.
        """

        # Mocking the methods
        static_info_repository = Mock()
        get_cut: Mock = static_info_repository.get_cut
        get_cut.return_value = empty_queryset(model=CuttingTechnique)
        change_status: Mock = static_info_repository.change_status
        uses_cuts_repository = Mock()
        get_uses_cut: Mock = uses_cuts_repository.get
        update_uses_cut: Mock = uses_cuts_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(ResourceNotFoundAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.change_cut_status(cut_code=cut_code, new_status=new_status)

        # Assert that the methods were not called
        change_status.assert_not_called()
        get_uses_cut.assert_not_called()
        update_uses_cut.assert_not_called()

    @pytest.mark.parametrize(
        argnames="cut_code, new_status",
        argvalues=[("laser_fibra", True)],
        ids=["router_cnc"],
    )
    def test_if_status_error(
        self,
        cut_code: str,
        new_status: bool,
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for changing the status of a cutting technique in
        the database when the status is the same as the new status.
        """

        # Prepare the appropriate scenario in the database
        cut = CuttingTechnique.objects.filter(code=cut_code).first()
        cut.is_active = new_status
        cut.save()

        # Mocking the methods
        uses_cuts_repository = Mock()
        get_uses_cut: Mock = uses_cuts_repository.get
        update_uses_cut: Mock = uses_cuts_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(StaticInfoAPIError):
            use_case = self.application_class(
                static_info_repository=StaticInfoRepository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.change_cut_status(cut_code=cut_code, new_status=new_status)

        # Assert that the methods were not called
        get_uses_cut.assert_not_called()
        update_uses_cut.assert_not_called()

        # Asserting that response data is correct
        cut = CuttingTechnique.objects.filter(code=cut_code).first()

        assert cut.is_active == new_status

    def test_if_conection_db_failed(self) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a DatabaseConnectionAPIError exception is raised.
        """

        # Mocking the methods
        static_info_repository = Mock()
        get_cut: Mock = static_info_repository.get_cut
        get_cut.side_effect = DatabaseConnectionAPIError
        change_status: Mock = static_info_repository.change_status
        uses_cuts_repository = Mock()
        get_uses_cut: Mock = uses_cuts_repository.get
        update_uses_cut: Mock = uses_cuts_repository.update

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository,
                uses_cuts_repository=uses_cuts_repository,
            )
            use_case.change_cut_status(cut_code="cut_code", new_status=True)

        # Assert that the methods were not called
        change_status.assert_not_called()
        get_uses_cut.assert_not_called()
        update_uses_cut.assert_not_called()
