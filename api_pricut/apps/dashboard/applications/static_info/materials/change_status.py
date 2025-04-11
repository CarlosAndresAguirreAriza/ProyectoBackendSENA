from apps.dashboard.domain.constants import DEACTIVATE_CUTTING
from apps.dashboard.domain.entities import ThicknessMaterial
from apps.dashboard.domain.interfaces import (
    IStaticInfoRepository,
    IUsesCutsRepository,
)
from apps.exceptions import ResourceNotFoundAPIError, StaticInfoAPIError
from apps.utils import StaticInfoErrorMessages
from ..utils import CutCompatibilityManager
from django.db.models import QuerySet


# Error messages
MATERIAL_NOT_FOUND = StaticInfoErrorMessages.MATERIAL_NOT_FOUND.value
STATUS_ERROR = StaticInfoErrorMessages.STATUS_ERROR.value


class UseCaseChangeMaterialStatus:
    """
    Use case responsible for changing the status of a material in the database.

    This class interacts with repositories injected as dependencies to get and
    update the state of a material, and manages cutting compatibility changes.
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

    def change_material_status(self, material_code: str, new_status: bool) -> None:
        """
        Changes the status of a material in the database.

        #### Parameters:
        - material_code: the code of the material to be updated.
        - new_status: the new status of the material.

        #### Raises:
        - ResourceNotFoundAPIError: If the material not found in the database.
        - StaticInfoAPIError: If the material status is the same as the new status.
        """

        material = self.__static_info_repository.get_material(
            filters={"code": material_code},
            section="thicknesses",
        ).first()

        if material is None:
            raise ResourceNotFoundAPIError(
                code=MATERIAL_NOT_FOUND["code"],
                detail=MATERIAL_NOT_FOUND["detail"],
            )
        elif material.is_active == new_status:
            raise StaticInfoAPIError(
                code=STATUS_ERROR["code"],
                detail=STATUS_ERROR["detail"],
            )

        all_thicknesses = material.thicknesses.all()
        self.__static_info_repository.change_status(
            instance=material,
            value=new_status,
        )
        self.__process_compatibility_cut(
            thicknesses=all_thicknesses,
            new_status=new_status,
        )

    def __process_compatibility_cut(
        self,
        new_status: bool,
        thicknesses: QuerySet[ThicknessMaterial],
    ) -> None:
        """
        Process the data in the `cutting compatibilities` section of the thickness
        information you want to update. Before performing the update, you must
        determine whether a cutting technique needs to be enabled or disabled.

        #### Parameters:
        - thicknesses: list of material thicknesses.
        """

        counter = {}
        uses_cuts = self.__uses_cuts_repository.get(all=True)

        # The cutting technique that was compatible with the thickness was
        # found to subtract one from the number of uses of the cut.
        for thickness in thicknesses:
            compatibility_cut = thickness.compatibility_cut

            for cut_code, compatibility in compatibility_cut.items():
                if compatibility is False:
                    continue
                if counter.get(cut_code, None) is None:
                    counter[cut_code] = 0
                if new_status is True:
                    counter[cut_code] += 1
                if new_status is False:
                    counter[cut_code] += -1

        for cut_code, num_uses in counter.items():
            # We iterate over all the previously obtained records to search for the
            # required record and avoid making extra queries to the database.
            for use in uses_cuts:
                if use.cut.code != cut_code:
                    continue

                cut_status = self.__uses_cuts_repository.update(
                    num_uses=num_uses,
                    instance=use,
                )

                if cut_status == DEACTIVATE_CUTTING:
                    self.__modified_thicknesses = True
                    manager = CutCompatibilityManager(
                        static_info_repository=self.__static_info_repository
                    )
                    manager.adjust_cut_compatibility(remove_cut=cut_code)
