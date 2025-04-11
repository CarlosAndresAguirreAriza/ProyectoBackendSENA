from apps.dashboard.domain.interfaces import IStaticInfoRepository
from apps.dashboard.domain.entities import CuttingTechnique
from apps.exceptions import ResourceNotFoundAPIError
from apps.utils import StaticInfoErrorMessages
from django.db.models import QuerySet
from typing import Dict, Any


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value


class UseCaseRetrieveCut:
    """
    Use case responsible for retrieving cutting technique data from the database.

    This class interacts with repositories injected as dependencies to retrieve
    cutting technique information from the database.
    """

    def __init__(self, static_info_repository: IStaticInfoRepository) -> None:
        self.__static_info_repository = static_info_repository

    def get_cut(self, filters: Dict[str, Any]) -> QuerySet[CuttingTechnique]:
        """
        Retrieves the cutting technique from the database.

        #### Parameters:
        - filters: the filters to be applied to the query.

        #### Raises:
        - ResourceNotFoundAPIError: If the cutting technique is not found.
        """

        cuts = self.__static_info_repository.get_cut(
            all_sections=True,
            filters=filters,
        )

        if cuts.first() is None:
            raise ResourceNotFoundAPIError(
                code=CUT_NOT_FOUND["code"],
                detail=CUT_NOT_FOUND["detail"],
            )

        return cuts
