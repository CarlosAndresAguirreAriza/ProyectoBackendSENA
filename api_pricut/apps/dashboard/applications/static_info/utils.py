from apps.dashboard.domain.interfaces import IStaticInfoRepository


class CutCompatibilityManager:
    """
    Manages cutting technique compatibility for each material thickness. This
    class interacts with `IStaticInfoRepository` to update cutting technique
    compatibility for materials.
    """

    def __init__(self, static_info_repository: IStaticInfoRepository) -> None:
        """
        Initialize the `CutCompatibilityManager` util.

        #### Parameters:
        - static_info_repository: The static info repository to use for
        database operations.
        """

        self.__static_info_repository = static_info_repository

    def adjust_cut_compatibility(
        self,
        remove_cut: str = None,
        add_cut: str = None,
    ) -> None:
        """
        Adjusts information about the compatibility of a cutting technique for
        all thicknesses of each available material, removing the cut that has
        been disabled or adding it if it has been reactivated.
        """

        if not (add_cut or remove_cut):
            raise ValueError(
                "You must provide a cutting technique to add or remove."
            )

        all_thicknesses = self.__static_info_repository.get_thickness(all=True)

        if remove_cut:
            for thickness in all_thicknesses:
                compatibility_cut = thickness.compatibility_cut
                compatibility_cut.pop(remove_cut)
                self.__static_info_repository.update_thickness(
                    data={"compatibility_cut": compatibility_cut},
                    instance=thickness,
                )
        elif add_cut:
            for thickness in all_thicknesses:
                compatibility_cut = thickness.compatibility_cut
                if compatibility_cut.get(add_cut, None):
                    continue

                compatibility_cut = {add_cut: False, **compatibility_cut}
                self.__static_info_repository.update_thickness(
                    data={"compatibility_cut": compatibility_cut},
                    instance=thickness,
                )
