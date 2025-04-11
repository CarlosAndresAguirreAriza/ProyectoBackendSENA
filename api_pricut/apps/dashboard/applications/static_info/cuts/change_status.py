from apps.dashboard.applications.static_info.utils import CutCompatibilityManager
from apps.dashboard.domain.interfaces import (
    IStaticInfoRepository,
    IUsesCutsRepository,
)
from apps.exceptions import ResourceNotFoundAPIError, StaticInfoAPIError
from apps.utils import StaticInfoErrorMessages


# Error messages
CUT_NOT_FOUND = StaticInfoErrorMessages.CUT_NOT_FOUND.value
STATUS_ERROR = StaticInfoErrorMessages.STATUS_ERROR.value


class UseCaseChangeCutStatus:
    """
    Use case responsible for changing the status of a cutting technique in the database.

    This class interacts with repositories injected as dependencies to get and
    update the state of a cutting technique, and manages cutting compatibility changes.
    """

    def __init__(
        self,
        static_info_repository: IStaticInfoRepository,
        uses_cuts_repository: IUsesCutsRepository,
    ) -> None:
        self.__static_info_repository = static_info_repository
        self.__uses_cuts_repository = uses_cuts_repository
        self.__modified_thicknesses = False

    @property
    def modified_thicknesses(self) -> bool:
        """
        Returns whether the information for all thicknesses existing in the
        database has been modified.
        """

        return self.__modified_thicknesses

    def change_cut_status(self, cut_code: str, new_status: bool) -> None:
        """
        Change the status of a cutting technique.

        #### Parameters:
        - cut_code: the code of the cutting technique to be updated.
        - new_status: the new status of the cutting technique.

        #### Raises:
        - ResourceNotFoundAPIError: If the cutting technique not found in the database.
        - StaticInfoAPIError: If the cutting technique is already in the desired state.
        """

        cut = self.__static_info_repository.get_cut(
            filters={"code": cut_code},
            section="base_info",
        ).first()

        if cut is None:
            raise ResourceNotFoundAPIError(
                code=CUT_NOT_FOUND["code"],
                detail=CUT_NOT_FOUND["detail"],
            )
        elif cut.is_active == new_status:
            raise StaticInfoAPIError(
                code=STATUS_ERROR["code"],
                detail=STATUS_ERROR["detail"],
            )
        elif new_status is False:
            self.__process_compatibility_cut(cut_code=cut.code)
        else:
            self.__static_info_repository.change_status(
                value=new_status,
                instance=cut,
            )

    def __process_compatibility_cut(self, cut_code: str) -> None:
        """
        Process the compatibility of the cutting technique with the materials.

        #### Parameters:
        - cut_code: the code of the cutting technique to be processed.
        """

        uses_cut = self.__uses_cuts_repository.get(cut_code=cut_code).first()
        manager = CutCompatibilityManager(
            static_info_repository=self.__static_info_repository
        )
        self.__uses_cuts_repository.update(
            num_uses=(uses_cut.number_uses) * -1,
            instance=uses_cut,
        )
        self.__modified_thicknesses = True
        manager.adjust_cut_compatibility(remove_cut=cut_code)
