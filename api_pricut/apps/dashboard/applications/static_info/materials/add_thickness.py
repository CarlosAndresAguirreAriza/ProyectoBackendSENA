from apps.dashboard.applications.static_info.utils import CutCompatibilityManager
from apps.dashboard.domain.interfaces import (
    IStaticInfoRepository,
    IUsesCutsRepository,
)
from apps.dashboard.domain.entities import ThicknessMaterial
from apps.dashboard.domain.constants import REACTIVATE_CUTTING
from apps.exceptions import ResourceNotFoundAPIError, StaticInfoAPIError
from apps.utils import StaticInfoErrorMessages
from typing import Dict, Any


# Error messages
MATERIAL_NOT_FOUND = StaticInfoErrorMessages.MATERIAL_NOT_FOUND.value
NOT_ADD_THICKNESS = StaticInfoErrorMessages.NOT_ADD_THICKNESS.value


class UseCaseAddThickness:
    """
    Use case responsible for adding material thickness data to the database.

    This class interacts with repositories injected as dependencies to create
    and manage thickness information, and adjusts cutting compatibility for
    each thickness of a material when a cut is reactivated.
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

    def add_thickness(
        self,
        material_code: str,
        data: Dict[str, Any],
    ) -> ThicknessMaterial:
        """
        Creates a new thickness for a material in the database.

        #### Parameters:
        - material_code: the code of the material to which the thickness belongs.
        - data: the thickness data to be added.

        #### Raises:
        - ResourceNotFoundAPIError: If the material not found in the database.
        - StaticInfoAPIError: If the cut is not active and cannot be added.
        """

        material = self.__static_info_repository.get_material(
            filters={"code": material_code},
            section="base_info",
        ).first()

        if material is None:
            raise ResourceNotFoundAPIError(
                code=MATERIAL_NOT_FOUND["code"],
                detail=MATERIAL_NOT_FOUND["detail"],
            )

        cut_codes = data["compatibility_cut"].keys()
        cuts = self.__static_info_repository.get_cut(
            filters={"code__in": list(cut_codes)},
            section="base_info",
        )

        for cut in cuts:
            if cut.is_active is False:
                raise StaticInfoAPIError(
                    code=NOT_ADD_THICKNESS["code"],
                    detail=NOT_ADD_THICKNESS["detail"],
                )

        thickness = self.__static_info_repository.add_thickness(
            material=material,
            data=data,
        )
        self.__process_compatibility_cut(instance=thickness)

        return thickness

    def __process_compatibility_cut(self, instance: ThicknessMaterial) -> None:
        """
        Adjusts the compatibility of a cutting technique for all thicknesses of
        each available material, adding the cut that has been reactivated.

        #### Parameters:
        - instance: the thickness instance that was added.
        """

        for cut_code, compatibility in instance.compatibility_cut.items():
            if not compatibility:
                continue

            uses_cut = self.__uses_cuts_repository.get(cut_code=cut_code).first()
            cut_status = self.__uses_cuts_repository.update(
                instance=uses_cut,
                num_uses=1,
            )

            if cut_status == REACTIVATE_CUTTING:
                self.__modified_thicknesses = True
                manager = CutCompatibilityManager(
                    static_info_repository=self.__static_info_repository
                )
                manager.adjust_cut_compatibility(add_cut=cut_code)
