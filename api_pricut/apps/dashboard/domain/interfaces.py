from apps.dashboard.models import (
    ThicknessMaterial,
    CuttingTechnique,
    MaterialCategory,
    UsesCuts,
    Material,
)
from django.db.models import QuerySet, Model
from abc import ABC, abstractmethod
from typing import Dict, List, Any


class IThicknessMaterialRepository(ABC):
    """
    ThicknessMaterialRepository interface.

    This interface defines the contract for a repository that manages
    `ThicknessMaterial` entity in the database. This class provides
    methods that perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def get_thickness(
        cls,
        all: bool = False,
        filters: Dict[str, Any] = None,
    ) -> QuerySet[ThicknessMaterial]:
        """
        Retrieves thicknesses filtered by the given parameters.

        #### Parameters:
            - all: If True, retrieves all thicknesses.
            - filters: A dictionary of filters to apply to the query.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def create_thicknesses(
        cls,
        material: Material,
        data: List[Dict[str, Any]],
    ) -> None:
        """
        Creates new thicknesses for a material in the database.

        #### Parameters:
            - material: An instance of the `Material` model that the thicknesses belong to.
            - data: A list of dictionaries with the data to create the thicknesses.
        """

        pass

    @classmethod
    @abstractmethod
    def add_thickness(
        cls,
        material: Material,
        data: Dict[str, Any],
    ) -> ThicknessMaterial:
        """
        Creates a new thickness for a material in the database.

        #### Parameters:
            - material: An instance of the Material model that the thickness belongs to.
            - data: A dictionary with the data to create the thickness.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def update_thickness(
        self,
        instance: ThicknessMaterial,
        data: Dict[str, Any],
    ) -> ThicknessMaterial:
        """
        Updates a thickness of a material in the database.

        #### Parameters:
            - instance: An instance of the `ThicknessMaterial` model that will be updated.
            - data: A dictionary with the data to update the thickness.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def delete_thickness(self, instance: ThicknessMaterial) -> None:
        """
        Deletes a thickness of a material from the database.

        #### Parameters:
            - instance: An instance of the `ThicknessMaterial` model to delete.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass


class IMaterialRepository(ABC):
    """
    MaterialRepository interface.

    This interface defines the contract for a repository that manages
    `Material` entity in the database. This class provides methods that
    perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def get_material(
        cls,
        filters: Dict[str, Any],
        section: str = None,
        all_sections: bool = False,
    ) -> QuerySet[Material]:
        """
        Retrieve material data from the database based on filters and the section
        of information requested.

        #### Parameters:
            - filters: A dictionary of filters to apply to the query.
            - section: The section of the material data to retrieve. Can be `descriptions`, `images`, or `base_info`.
            - all_sections: If True, retrieves all sections of the material data.

        #### Raises:
            - ValueError: If an invalid section is provided.
            - DatabaseConnectionAPIError: If there is an operational error with the database.
        """

        pass

    @classmethod
    @abstractmethod
    def create_material(
        cls,
        category: MaterialCategory,
        data: Dict[str, Any],
    ) -> Material:
        """
        Creates a new material in the database.

        #### Parameters:
            - category: An instance of the `MaterialCategory` model that the material
            belongs to.
            - data: A dictionary with the data to create the material.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def update_descriptions(
        cls,
        instance: Material,
        data: Dict[str, Any],
    ) -> Material:
        """
        Updates the descriptions of a material in the database.

        #### Parameters:
            - instance: An instance of the `Material` model to update.
            - data: A dictionary with the data to update the material.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with
            the database.
        """

        pass

    @classmethod
    @abstractmethod
    def update_images(
        cls,
        instance: Material,
        data: Dict[str, Any],
    ) -> Material:
        """
        Updates the images of a material in the database.

        #### Parameters:
            - instance: An instance of the `Material` model to update.
            - data: A dictionary with the data to update the material.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def deactivate_material(cls, instance: Material) -> Material:
        """
        Deactivates a material in the database.

        #### Parameters:
            - instance: An instance of the `Material` model to deactivate.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass


class ICuttingTechniqueRepository(ABC):
    """
    CuttingTechniqueRepository interface.

    This interface defines the contract for a repository that manages
    `CuttingTechnique` entity in the database. This class provides methods
    that perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def get_cut(
        cls,
        filters: Dict[str, Any],
        section: str = None,
        all_sections: bool = False,
    ) -> QuerySet[CuttingTechnique]:
        """
        Retrieves cutting techniques filtered by the given parameters.

        #### Parameters:
            - filters: A dictionary of filters to apply to the query.
            - section: The section of the cutting technique data to retrieve. Can be `descriptions`, `images`, or `base_info`.
            - all_sections: If True, retrieves all sections of the cutting technique data.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def create_cut(cls, data: Dict[str, Any]) -> CuttingTechnique:
        """
        Creates a new cutting technique in the database.

        #### Parameters:
            - data: A dictionary with the data to create the cutting technique.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def update_cut(
        self,
        instance: CuttingTechnique,
        data: Dict[str, Any],
    ) -> CuttingTechnique:
        """
        Updates a cutting technique in the database.

        #### Parameters:
            - instance: An instance of the CuttingTechnique model that will be updated.
            - data: A dictionary with the data to update the cutting technique.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def deactivate_cut(
        cls,
        instance: CuttingTechnique,
    ) -> CuttingTechnique:
        """
        Deactivates a cutting technique in the database.

        #### Parameters:
            - instance: An instance of the `CuttingTechnique` model to deactivate.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass


class IMaterialCategoryRepository(ABC):
    """
    MaterialCategoryRepository interface.

    This interface defines the contract for a repository that manages
    `MaterialCategory` entity in the database. This class provides methods
    that perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def get_material_category(
        cls,
        filters: Dict[str, Any],
    ) -> QuerySet[MaterialCategory]:
        """
        Retrieves categories of materials filtered by the given parameters.

        #### Parameters:
            - filters: A dictionary of filters to apply to the query.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def create_material_category(cls, data: Dict[str, Any]) -> MaterialCategory:
        """
        Creates a new category of materials in the database.

        #### Parameters:
            - data: A dictionary with the data to create the category.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def deactivate_material_category(
        cls,
        instance: MaterialCategory,
    ) -> MaterialCategory:
        """
        Deactivates a category of materials in the database.

        #### Parameters:
            - instance: An instance of the `MaterialCategory` model to deactivate.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass


class IStaticInfoRepository(
    IThicknessMaterialRepository,
    ICuttingTechniqueRepository,
    IMaterialCategoryRepository,
    IMaterialRepository,
):
    """
    StaticInfoRepository interface.

    This interface defines the contract for a repository that manages
    static information in the database. This class provides methods that
    perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def exists(cls, data_type: str, data: Dict[str, Any]) -> bool:
        """
        Checks if there is data in the database.

        #### Parameters:
            - data_type: The type of data to check if it exists in the database. It can be `material_category`, `cut`, or `material`.
            - data: A dictionary with the data to check.

        #### Raises:
            - ValueError: If the data type is invalid.
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def change_status(cls, instance: Model, value: bool) -> None:
        """
        Changes the status of an instance of the static information in the database.

        #### Parameters:
            - instance: An instance of a model to change the status.
            - value: The new status value.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass


class IUsesCutsRepository(ABC):
    """
    UsesCutsRepository interface.

    This interface defines the contract for a repository that manages
    `UsesCuts` entity in the database. This class provides methods that
    perform CRUD operations among other types of queries.
    """

    @classmethod
    @abstractmethod
    def get(cls, cut_code: str = None, all: bool = False) -> QuerySet[UsesCuts]:
        """
        Retrieves all the information about the uses of each cutting technique in
        different materials.

        #### Parameters:
            - cut_code: The code of the cutting technique to filter the query.
            - all: If True, retrieves all records.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def create(cls, cut: CuttingTechnique, num_uses: int) -> None:
        """
        Creates a new record of the number of uses of a cutting technique in the
        database.

        #### Parameters:
            - cut: An instance of the CuttingTechnique model that the number of uses belongs to.
            - num_uses: The number of uses of the cutting technique

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass

    @classmethod
    @abstractmethod
    def update(cls, num_uses: int, instance: UsesCuts) -> str:
        """
        Updates the number of uses of a cutting technique in the database.

            - If the number of uses reaches zero, the cutting technique is deactivated.
            - If a deactivated cutting technique increases its number of uses, it is
            activated again.

        #### Parameters:
            - num_uses: The number of uses to add to the current number of uses.
            - instance: An instance of the UsesCuts model that will be updated.

        #### Returns:
        A dictionary with the status of the cutting technique and its code if the status changes.
        Possible keys in the dictionary are:

            - status: Either REACTIVATE_CUTTING or DEACTIVATE_CUTTING.

        #### Raises:
            - DatabaseConnectionAPIError: If there is an operational error with the
            database.
        """

        pass
