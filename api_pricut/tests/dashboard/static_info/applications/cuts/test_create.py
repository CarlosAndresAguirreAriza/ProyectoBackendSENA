from apps.dashboard.infrastructure import StaticInfoRepository
from apps.dashboard.applications import UseCaseCreateCut
from apps.dashboard.domain.entities import CuttingTechnique
from apps.exceptions import DatabaseConnectionAPIError
from apps.utils import standardize_and_replace
from unittest.mock import Mock
from typing import Dict, Any
import pytest


@pytest.mark.django_db
class TestCreateCutApplication:
    """
    This class encapsulates the tests for the use case or business logic
    responsible for creating a cutting technique.
    """

    application_class = UseCaseCreateCut

    @pytest.mark.parametrize(
        argnames="data",
        argvalues=[
            {
                "name": "Nombre del servicio",
                "about_text": "Descripción del servicio.",
                "card_text": "Descripción de la tarjeta servicio.",
                "common_uses_text": "Usos comunes del servicio.",
                "main_text": "Texto principal del servicio.",
                "banner_image": "https://image.png",
                "card_image": "https://image.png",
                "main_image": "https://image.png",
                "about_image": "https://image.png",
                "uses_image": "https://image.png",
            },
        ],
        ids=["valid_data"],
    )
    def test_if_create_cut(self, data: Dict[str, Any]) -> None:
        """
        This test is responsible for validating the expected behavior of the
        use case responsible for creating a cutting technique.
        """

        # Asserting that the user does not exist in the database
        assert CuttingTechnique.objects.filter(name=data["name"]).exists() is False

        # Instantiating the application and calling the method
        use_case = self.application_class(
            static_info_repository=StaticInfoRepository
        )
        cut = use_case.create_cut(data=data)

        # Asserting that the correct data
        assert cut.name == data["name"]
        assert cut.code == standardize_and_replace(text=data["name"])
        assert cut.about_text == data["about_text"]
        assert cut.common_uses_text == data["common_uses_text"]
        assert cut.main_text == data["main_text"]
        assert cut.banner_image == data["banner_image"]
        assert cut.main_image == data["main_image"]
        assert cut.about_image == data["about_image"]
        assert cut.uses_image == data["uses_image"]
        assert cut.is_active == False

    @pytest.mark.parametrize(
        argnames="data",
        argvalues=[
            {
                "name": "Nombre del servicio",
                "about_text": "Descripción del servicio.",
                "card_text": "Descripción de la tarjeta servicio.",
                "common_uses_text": "Usos comunes del servicio.",
                "main_text": "Texto principal del servicio.",
                "banner_image": "https://image.png",
                "card_image": "https://image.png",
                "main_image": "https://image.png",
                "about_image": "https://image.png",
                "uses_image": "https://image.png",
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
        create_cut: Mock = static_info_repository.create_cut
        create_cut.side_effect = DatabaseConnectionAPIError

        # Instantiating the application and calling the method
        with pytest.raises(DatabaseConnectionAPIError):
            use_case = self.application_class(
                static_info_repository=static_info_repository
            )
            use_case.create_cut(data=data)

        # Asserting that the cutting technique was not created
        assert CuttingTechnique.objects.count() == 0
