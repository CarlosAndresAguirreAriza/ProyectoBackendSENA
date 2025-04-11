from apps.dashboard.domain.interfaces import IStaticInfoRepository
from apps.dashboard.domain.entities import CuttingTechnique
from apps.utils import standardize_and_replace
from typing import Dict, Any


class UseCaseCreateCut:
    """
    Use case responsible for creating a new cutting technique in the database.

    This class interacts with repositories injected as dependencies to create
    a new cutting technique in the database.
    """

    def __init__(self, static_info_repository: IStaticInfoRepository) -> None:
        self.__static_info_repository = static_info_repository

    def create_cut(self, data: Dict[str, Any]) -> CuttingTechnique:
        """
        Creates a new cutting technique in the database.

        #### Parameters:
        - data: the data to be used to create the cutting technique.
        """

        data["code"] = standardize_and_replace(text=data["name"])

        return self.__static_info_repository.create_cut(data=data)
