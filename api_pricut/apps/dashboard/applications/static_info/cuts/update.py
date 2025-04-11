from apps.dashboard.domain.interfaces import IStaticInfoRepository
from apps.dashboard.models import CuttingTechnique
from apps.exceptions import ResourceNotFoundAPIError
from apps.utils import StaticInfoErrorMessages, standardize_and_replace
from typing import Dict, Any


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value


class UseCaseUpdateCut:
    """
    Use case responsible for updating a cutting technique in the database.

    This class interacts with repositories injected as dependencies to update
    a cutting technique in the database.
    """

    def __init__(self, static_info_repository: IStaticInfoRepository) -> None:
        self.__static_info_repository = static_info_repository

    def update_cut_baseinfo(
        self,
        cut_code: str,
        data: Dict[str, Any],
    ) -> CuttingTechnique:
        """
        Update cutting technique in the database.

        #### Parameters
        - cut_code: the code of the cutting technique to be updated.
        - data: the data to be updated.

        #### Raises
        - ResourceNotFoundAPIError: If the cutting technique is not found.
        """

        cut = self.__static_info_repository.get_cut(
            filters={"code": cut_code},
            section="base_info",
        ).first()

        name = data.get("name", None)

        if name is not None:
            data["code"] = standardize_and_replace(text=name)

        if cut is None:
            raise ResourceNotFoundAPIError(
                code=CUT_NOT_FOUND["code"],
                detail=CUT_NOT_FOUND["detail"],
            )

        return self.__static_info_repository.update_cut(
            instance=cut,
            data=data,
        )

    def update_cut_descriptions(
        self,
        cut_code: str,
        data: Dict[str, Any],
    ) -> CuttingTechnique:
        """
        Update cutting technique in the database.

        #### Parameters
        - cut_code: the code of the cutting technique to be updated.
        - data: the data to be updated.

        #### Raises
        - ResourceNotFoundAPIError: If the cutting technique is not found.
        """

        cut = self.__static_info_repository.get_cut(
            filters={"code": cut_code},
            section="descriptions",
        ).first()

        if cut is None:
            raise ResourceNotFoundAPIError(
                code=CUT_NOT_FOUND["code"],
                detail=CUT_NOT_FOUND["detail"],
            )

        return self.__static_info_repository.update_cut(
            instance=cut,
            data=data,
        )
