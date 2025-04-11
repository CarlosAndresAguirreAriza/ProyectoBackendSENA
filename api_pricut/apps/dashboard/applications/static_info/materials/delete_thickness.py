from apps.dashboard.applications.static_info.utils import CutCompatibilityManager
from apps.dashboard.domain.constants import DEACTIVATE_CUTTING
from apps.dashboard.domain.entities import ThicknessMaterial
from apps.dashboard.domain.interfaces import (
    IStaticInfoRepository,
    IUsesCutsRepository,
)
from apps.exceptions import ResourceNotFoundAPIError
from apps.utils import StaticInfoErrorMessages


# Error messages
THICKNESS_NOT_FOUND = StaticInfoErrorMessages.THICKNESS_NOT_FOUND.value


class UseCaseDeleteThickness:
    """
    Use case responsible for deleting a thickness from the database.

    This class interacts with repositories injected as dependencies to obtain
    and delete thickness information, and manages cutting compatibility changes.
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

    def delete_thickness(self, thickness_id: int) -> None:
        """
        Deletes a thickness of a material from the database.

        #### Parameters:
        - thickness_id: the identifier of the thickness to be deleted.

        #### Raises:
        - ResourceNotFoundAPIError: If the thickness not found in the database.
        """

        thickness = self.__static_info_repository.get_thickness(
            filters={"id": thickness_id},
        ).first()

        if thickness is None:
            raise ResourceNotFoundAPIError(
                code=THICKNESS_NOT_FOUND["code"],
                detail=THICKNESS_NOT_FOUND["detail"],
            )

        self.__static_info_repository.delete_thickness(instance=thickness)
        self.__process_compatibility_cut(instance=thickness)

    def __process_compatibility_cut(self, instance: ThicknessMaterial) -> None:
        """
        Process the compatibility of the cutting techniques with the thickness
        to update the number of uses of the cutting technique.

        #### Parameters:
        - instance: the thickness instance that was deleted.
        """

        counter = {}
        uses_cuts = self.__uses_cuts_repository.get(all=True)

        # The cutting technique that was compatible with the thickness was
        # found to subtract one from the number of uses of the cut.
        for cut_code, compatibility in instance.compatibility_cut.items():
            if not compatibility:
                continue

            counter[cut_code] = -1

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
