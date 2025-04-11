from apps.dashboard.applications.static_info.utils import CutCompatibilityManager
from apps.dashboard.domain.interfaces import (
    IStaticInfoRepository,
    IUsesCutsRepository,
)
from apps.dashboard.domain.constants import (
    REACTIVATE_CUTTING,
    DEACTIVATE_CUTTING,
    NO_CHANGE_CUTTING,
)
from apps.dashboard.domain.entities import ThicknessMaterial
from apps.exceptions import StaticInfoAPIError, ResourceNotFoundAPIError
from apps.utils import StaticInfoErrorMessages
from typing import Dict, Any
from deepdiff import DeepDiff


# Error messages
CHANGES_NOT_DETECTED = StaticInfoErrorMessages.CHANGES_NOT_DETECTED.value
NOT_ADD_THICKNESS = StaticInfoErrorMessages.NOT_ADD_THICKNESS.value
THICKNESS_NOT_FOUND = StaticInfoErrorMessages.THICKNESS_NOT_FOUND.value
REMOVE_CUT_COMPATIBILITY = StaticInfoErrorMessages.REMOVE_CUT_COMPATIBILITY.value
CUT_COMPATIBILITY = StaticInfoErrorMessages.CUT_COMPATIBILITY.value


class UseCaseUpdateThickness:
    """
    Use case responsible for updating material thickness data in the database.

    This class interacts with repositories injected as dependencies to obtain
    and update thickness information, and manages cutting compatibility changes.
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

    def update_thickness(
        self,
        thickness_id: int,
        data: Dict[str, Any],
    ) -> ThicknessMaterial:
        """
        Updates a thickness for a material in the database.

        #### Parameters:
        - thickness_id: the identifier of the thickness to be updated.
        - data: the thickness data to be updated.

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

        data["compatibility_cut"] = self.__process_changes(
            original_data=thickness.compatibility_cut,
            modified_data=data["compatibility_cut"],
        )

        return self.__static_info_repository.update_thickness(
            instance=thickness,
            data=data,
        )

    def __process_changes(
        self,
        original_data: Dict[str, bool],
        modified_data: Dict[str, bool],
    ) -> Dict[str, bool]:
        """
        Process the data in the `cutting compatibilities` section of the thickness
        information you want to update. Before performing the update, you must
        determine whether a cutting technique needs to be enabled or disabled.

        #### Parameters:
        - original_data: the original cutting compatibility data.
        - modified_data: the modified cutting compatibility data.
        """

        # Calculate the difference in cut compatibility
        # Determines the number of times a cut lost or gained compatibility
        counter = self.__calculate_cut_compat_changes(
            original_data=original_data,
            modified_data=modified_data,
        )
        uses_cuts = self.__uses_cuts_repository.get(all=True)

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

                if cut_status != NO_CHANGE_CUTTING:
                    manager = CutCompatibilityManager(
                        static_info_repository=self.__static_info_repository
                    )

                    if cut_status == REACTIVATE_CUTTING:
                        self.__modified_thicknesses = True
                        manager.adjust_cut_compatibility(add_cut=cut_code)

                        # Add the reactivated cut to thickness compatible cuts information
                        # Applying this setting allows for an easier update
                        modified_data[cut_code] = True
                    elif cut_status == DEACTIVATE_CUTTING:
                        self.__modified_thicknesses = True
                        manager.adjust_cut_compatibility(remove_cut=cut_code)

                        # Remove disabled cutting from thickness compatible cutting information
                        # Applying this setting allows for an easier update
                        modified_data.pop(cut_code)

        return modified_data

    def __calculate_cut_compat_changes(
        self,
        original_data: Dict[str, bool],
        modified_data: Dict[str, bool],
    ) -> Dict[str, int]:
        """
        Reads the modified information from the material thicknesses section and
        compares it to the original information, to count the number of times a
        cutting technique was added as compatible or not.

        #### Parameters:
        - original_data: the original cutting compatibility data.
        - modified_data: the modified cutting compatibility data.

        #### Raises
        - StaticInfoAPIError: If you attempt to make a modification to the material
        information that is not permitted.
        """

        diff_data = DeepDiff(t1=original_data, t2=modified_data)

        if not bool(diff_data):
            raise StaticInfoAPIError(detail=CHANGES_NOT_DETECTED)
        elif diff_data.get("dictionary_item_removed", None):
            raise StaticInfoAPIError(detail=REMOVE_CUT_COMPATIBILITY)

        return self.__get_usage_counter(
            modified_data=modified_data,
            diff=diff_data,
        )

    @staticmethod
    def __get_usage_counter(
        diff: DeepDiff,
        modified_data: Dict[str, bool],
    ) -> Dict[str, int]:
        """
        Updates the counter based on the detected differences.

        #### Parameters:
        - diff: the differences detected between the original and modified data.
        - modified_data: the modified cutting compatibility data.
        """

        counter = {}

        if diff.get("values_changed", None):
            new_data = diff["values_changed"]

            for key_path in new_data:
                key = key_path.replace("root[", "").replace("]", "").strip("'")

                if not counter.get(key, None):
                    counter[key] = 0

                new_value = modified_data[key]

                # If the cutting technique became compatible with the material
                # +1 is added to the number of uses of the cut.
                # If the cutting technique is no longer compatible with the material,
                # -1 is added to the number of uses of the cut.
                counter[key] += 1 if new_value else -1
        if diff.get("dictionary_item_added", None):
            new_data = diff["dictionary_item_added"]

            for key_path in new_data:
                key = key_path.replace("root[", "").replace("]", "").strip("'")

                if not counter.get(key, None):
                    counter[key] = 0

                new_value = modified_data[key]

                if not new_value:
                    raise StaticInfoAPIError(detail=CUT_COMPATIBILITY)

                # If the cutting technique became compatible with the material
                # +1 is added to the number of uses of the cut.
                counter[key] += 1

        return counter
