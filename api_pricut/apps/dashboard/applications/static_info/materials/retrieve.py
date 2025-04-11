from apps.dashboard.domain.interfaces import IStaticInfoRepository
from apps.dashboard.domain.entities import Material
from apps.exceptions import ResourceNotFoundAPIError
from apps.utils import StaticInfoErrorMessages
from django.db.models import QuerySet
from typing import Dict, Any


# Error messages
MATERIAL_NOT_FOUND = StaticInfoErrorMessages.MATERIAL_NOT_FOUND.value


class UseCaseRetrieveMaterial:
    """
    Use case responsible for retrieving material data from the database.

    This class interacts with repositories injected as dependencies to retrieve
    material information from the database.
    """

    def __init__(self, static_info_repository: IStaticInfoRepository) -> None:
        self.__static_info_repository = static_info_repository

    def get_material(self, filters: Dict[str, Any]) -> QuerySet[Material]:
        """
        Retrieves the material from the database.

        #### Parameters:
        - filters: the filters to be applied to the query.

        #### Raises:
        - ResourceNotFoundAPIError: If the material is not found.
        """

        materials = self.__static_info_repository.get_material(
            all_sections=True,
            filters=filters,
        )

        if materials.first() is None:
            raise ResourceNotFoundAPIError(
                code=MATERIAL_NOT_FOUND["code"],
                detail=MATERIAL_NOT_FOUND["detail"],
            )

        return materials
