from apps.dashboard.infrastructure.repositories import StaticInfoRepository
from apps.dashboard.applications import UseCaseUpdateCut
from apps.dashboard.domain.entities import CuttingTechnique
from apps.exceptions import DatabaseConnectionAPIError, ResourceNotFoundAPIError
from apps.utils import standardize_and_replace
from tests.utils import empty_queryset
from typing import Dict, Any
from unittest.mock import Mock
import pytest


@pytest.mark.django_db
class TestUpdateCutApplication:
    """
    This class encapsulates the tests for the use case or business logic
    responsible for updating a cutting technique.
    """

    application_class = UseCaseUpdateCut

    @pytest.mark.parametrize(
        argnames="cut_code, data",
        argvalues=[
            (
                "router_cnc",
                {
                    "base_info": {
                        "name": "Laser CNC",
                    },
                    "descriptions": {
                        "about_text": "Descripción de la técnica de corte.",
                        "common_uses_text": "Descripción de la tarjeta servicio.",
                        "main_text": "Acerca de la técnica de corte.",
                        "card_text": "Usos comunes de la técnica de corte.",
                    },
                    "images": {
                        "banner_image": "https://image.png",
                        "main_image": "https://image.png",
                        "card_image": "https://image.png",
                        "about_image": "https://image.png",
                        "uses_image": "https://image.png",
                    },
                },
            )
        ],
        ids=["valid_data"],
    )
    def test_if_update_cut(
        self,
        cut_code: str,
        data: Dict[str, Any],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when the request data is valid.
        """

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository
        )
        cut_base_info = use_case.update_cut_baseinfo(
            cut_code=cut_code,
            data=data["base_info"],
        )
        cut_description = use_case.update_cut_descriptions(
            cut_code=standardize_and_replace(text=data["base_info"]["name"]),
            data=data["descriptions"],
        )

        # Asserting that the user has the correct data
        base_info = data["base_info"]
        descriptions = data["descriptions"]

        assert cut_base_info.name == base_info["name"]
        assert cut_base_info.code == standardize_and_replace(
            text=base_info["name"]
        )
        assert cut_description.about_text == descriptions["about_text"]
        assert cut_description.card_text == descriptions["card_text"]
        assert cut_description.common_uses_text == descriptions["common_uses_text"]
        assert cut_description.main_text == descriptions["main_text"]

    @pytest.mark.parametrize(
        argnames="data",
        argvalues=[
            {
                "base_info": {
                    "name": "Laser CNC",
                },
                "descriptions": {
                    "about_text": "Descripción de la técnica de corte.",
                    "common_uses_text": "Descripción de la tarjeta servicio.",
                    "main_text": "Acerca de la técnica de corte.",
                    "card_text": "Usos comunes de la técnica de corte.",
                },
                "images": {
                    "banner_image": "https://image.png",
                    "main_image": "https://image.png",
                    "card_image": "https://image.png",
                    "about_image": "https://image.png",
                    "uses_image": "https://image.png",
                },
            },
        ],
        ids=["valid_data"],
    )
    def test_if_cut_not_found(
        self,
        data: Dict[str, Any],
        load_static_info,
    ) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when the cutting technique is not found.
        """

        # Mocking the methods
        static_info_repository = Mock()
        get_cut: Mock = static_info_repository.get_cut
        get_cut.return_value = empty_queryset(model=CuttingTechnique)
        update_cut: Mock = static_info_repository.update_cut

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=static_info_repository
        )
        with pytest.raises(ResourceNotFoundAPIError):
            use_case.update_cut_baseinfo(
                cut_code="other_cut",
                data=data["base_info"],
            )
            use_case.update_cut_descriptions(
                cut_code="other_cut",
                data=data["descriptions"],
            )

        # Asserting that the method was not called
        update_cut.assert_not_called()

    @pytest.mark.parametrize(
        argnames="data",
        argvalues=[
            {
                "base_info": {
                    "name": "Laser CNC",
                },
                "descriptions": {
                    "about_text": "Descripción de la técnica de corte.",
                    "common_uses_text": "Descripción de la tarjeta servicio.",
                    "main_text": "Acerca de la técnica de corte.",
                    "card_text": "Usos comunes de la técnica de corte.",
                },
                "images": {
                    "banner_image": "https://image.png",
                    "main_image": "https://image.png",
                    "card_image": "https://image.png",
                    "about_image": "https://image.png",
                    "uses_image": "https://image.png",
                },
            },
        ],
        ids=["valid_data"],
    )
    def test_if_conection_db_failed(self, data: Dict[str, Any]) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case when a DatabaseConnectionAPIError exception is raised.
        """

        # Mocking the methods
        static_info_repository = Mock()
        get_cut: Mock = static_info_repository.get_cut
        get_cut.side_effect = DatabaseConnectionAPIError
        update_cut: Mock = static_info_repository.update_cut

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=static_info_repository
        )
        with pytest.raises(DatabaseConnectionAPIError):
            use_case.update_cut_baseinfo(
                cut_code="other_cut",
                data=data["base_info"],
            )
        with pytest.raises(DatabaseConnectionAPIError):
            use_case.update_cut_descriptions(
                cut_code="other_cut",
                data=data["descriptions"],
            )

        # Asserting that the cutting technique was not created
        assert CuttingTechnique.objects.count() == 0

        # Asserting that the method was not called
        update_cut.assert_not_called()
