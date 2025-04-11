from apps.dashboard.domain.interfaces import (
    IThicknessMaterialRepository,
    ICuttingTechniqueRepository,
    IMaterialCategoryRepository,
    IStaticInfoRepository,
    IUsesCutsRepository,
    IMaterialRepository,
)
from apps.dashboard.domain.constants import (
    MaterialsDataProperties,
    CutDataProperties,
    REACTIVATE_CUTTING,
    DEACTIVATE_CUTTING,
    NO_CHANGE_CUTTING,
)
from apps.dashboard.domain.entities import (
    ThicknessMaterial,
    CuttingTechnique,
    MaterialCategory,
    UsesCuts,
    Material,
)
from apps.exceptions import DatabaseConnectionAPIError
from django.db import OperationalError
from django.db.models import QuerySet, Model
from typing import Dict, List, Any


# Constants
MATERIAL_SECTION_DESCRIPTIONS = MaterialsDataProperties.SECTION_DESCRIPTIONS.value
MATERIAL_SECTION_THICKNESS = MaterialsDataProperties.SECTION_THICKNESS.value
MATERIAL_SECTION_IMAGES = MaterialsDataProperties.SECTION_IMAGES.value
MATERIAL_SECTION_BASE = MaterialsDataProperties.SECTION_BASE.value
MATERIAL_DESCRIP_FIELDS = MaterialsDataProperties.DESCRIP_FIELDS.value
MATERIAL_IMAGE_FIELDS = MaterialsDataProperties.IMAGE_FIELDS.value
MATERIAL_BASE_FIELDS = MaterialsDataProperties.BASE_FIELDS.value
CUT_SECTION_DESCRIPTIONS = CutDataProperties.SECTION_DESCRIPTIONS.value
CUT_SECTION_IMAGES = CutDataProperties.SECTION_IMAGES.value
CUT_SECTION_BASE = CutDataProperties.SECTION_BASE.value
CUT_BASE_FIELDS = CutDataProperties.BASE_FIELDS.value
CUT_IMAGE_FIELDS = CutDataProperties.IMAGE_FIELDS.value
CUT_DESCRIP_FIELDS = CutDataProperties.DESCRIP_FIELDS.value


class ThicknessMaterialRepository(IThicknessMaterialRepository):
    """
    Repository class for managing `ThicknessMaterial` entity in the database.

    This class provides methods that perform CRUD operations among other types
    of queries. It handles operational errors in the database by generating a
    custom exception.
    """

    thickness_model = ThicknessMaterial

    @classmethod
    def get_thickness(
        cls,
        all: bool = False,
        filters: Dict[str, Any] = None,
    ) -> QuerySet[ThicknessMaterial]:

        try:
            if all:
                return cls.thickness_model.objects.select_related("material").all()

            # fmt: off
            return (
                cls.thickness_model.objects.
                filter(**filters)
                .select_related("material")
            )
            # fmt: on
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def create_thicknesses(
        cls,
        material: Material,
        data: List[Dict[str, Any]],
    ) -> None:

        try:
            objs = [
                cls.thickness_model(material=material, **thickness_data)
                for thickness_data in data
            ]
            cls.thickness_model.objects.bulk_create(objs=objs)
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def add_thickness(
        cls,
        material: Material,
        data: Dict[str, Any],
    ) -> ThicknessMaterial:

        try:
            return cls.thickness_model.objects.create(material=material, **data)
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def update_thickness(
        self,
        instance: ThicknessMaterial,
        data: Dict[str, Any],
    ) -> ThicknessMaterial:

        try:
            for key, value in data.items():
                setattr(instance, key, value)

            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def delete_thickness(self, instance: ThicknessMaterial) -> None:

        try:
            instance.delete()
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()


class MaterialRepository(IMaterialRepository):
    """
    A repository class for managing `Material` entity in the database.

    This class provides methods that perform CRUD operations among other types
    of queries. It handles operational errors in the database by generating a
    custom exception.
    """

    material_model = Material

    @classmethod
    def get_material(
        cls,
        filters: Dict[str, Any],
        section: str = None,
        all_sections: bool = False,
    ) -> QuerySet[Material]:

        try:
            query = cls.material_model.objects

            if all_sections:
                fields = (
                    MATERIAL_BASE_FIELDS
                    + MATERIAL_DESCRIP_FIELDS
                    + MATERIAL_IMAGE_FIELDS
                )

                return (
                    query.filter(**filters)
                    .select_related("category")
                    .prefetch_related("thicknesses")
                    .only(*fields)
                )
            elif section == MATERIAL_SECTION_DESCRIPTIONS:
                fields = MATERIAL_BASE_FIELDS + MATERIAL_DESCRIP_FIELDS

                return (
                    query.filter(**filters)
                    .select_related("category")
                    .only(*fields)
                )
            elif section == MATERIAL_SECTION_IMAGES:
                fields = MATERIAL_BASE_FIELDS + MATERIAL_IMAGE_FIELDS

                return (
                    query.filter(**filters)
                    .select_related("category")
                    .only(*fields)
                )
            elif section == MATERIAL_SECTION_THICKNESS:
                fields = MATERIAL_BASE_FIELDS

                return (
                    query.filter(**filters)
                    .select_related("category")
                    .prefetch_related("thicknesses")
                    .only(*fields)
                )
            elif section == MATERIAL_SECTION_BASE:
                fields = MATERIAL_BASE_FIELDS

                return (
                    query.filter(**filters)
                    .select_related("category")
                    .only(*fields)
                )

            sections = [
                MATERIAL_SECTION_DESCRIPTIONS,
                MATERIAL_SECTION_IMAGES,
                MATERIAL_SECTION_BASE,
            ]

            raise ValueError(f"Invalid section, must be {" or ".join(sections)}")
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def create_material(
        cls,
        category: MaterialCategory,
        data: Dict[str, Any],
    ) -> Material:

        try:
            return cls.material_model.objects.create(
                category=category,
                is_active=True,
                **data,
            )
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def update_descriptions(
        cls,
        instance: Material,
        data: Dict[str, Any],
    ) -> Material:

        try:
            for key, value in data.items():
                setattr(instance, key, value)

            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def update_images(
        cls,
        instance: Material,
        data: Dict[str, Any],
    ) -> Material:

        try:
            for key, value in data.items():
                setattr(instance, key, value)

            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def deactivate_material(cls, instance: Material) -> Material:

        try:
            instance.is_active = False
            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()


class CuttingTechniqueRepository(ICuttingTechniqueRepository):
    """
    Repository class for managing `CuttingTechnique` entity in the database.

    This class provides methods that perform CRUD operations among other types
    of queries. It handles operational errors in the database by generating a
    custom exception.
    """

    cutting_technique_model = CuttingTechnique

    @classmethod
    def get_cut(
        cls,
        filters: Dict[str, Any],
        section: str = None,
        all_sections: bool = False,
    ) -> QuerySet[CuttingTechnique]:

        try:
            query = cls.cutting_technique_model.objects

            if all_sections:
                fields = CUT_BASE_FIELDS + CUT_DESCRIP_FIELDS + CUT_IMAGE_FIELDS

                return query.filter(**filters).only(*fields)
            elif section == CUT_SECTION_DESCRIPTIONS:
                fields = CUT_BASE_FIELDS + CUT_DESCRIP_FIELDS

                return query.filter(**filters).only(*fields)
            elif section == CUT_SECTION_IMAGES:
                fields = CUT_BASE_FIELDS + CUT_IMAGE_FIELDS

                return query.filter(**filters).only(*fields)
            elif section == CUT_SECTION_BASE:
                fields = CUT_BASE_FIELDS

                return query.filter(**filters).only(*fields)

            sections = [
                CUT_SECTION_DESCRIPTIONS,
                CUT_SECTION_IMAGES,
                CUT_SECTION_BASE,
            ]

            raise ValueError(f"Invalid section, must be {" or ".join(sections)}")
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def create_cut(cls, data: Dict[str, Any]) -> CuttingTechnique:

        try:
            return cls.cutting_technique_model.objects.create(
                is_active=False,
                **data,
            )
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def update_cut(
        self,
        instance: CuttingTechnique,
        data: Dict[str, Any],
    ) -> CuttingTechnique:

        try:
            for key, value in data.items():
                setattr(instance, key, value)

            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def deactivate_cut(
        cls,
        instance: CuttingTechnique,
    ) -> CuttingTechnique:

        try:
            instance.is_active = False
            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()


class MaterialCategoryRepository(IMaterialCategoryRepository):
    """
    Repository class for managing `MaterialCategory` entity in the database.

    This class provides methods that perform CRUD operations among other types
    of queries. It handles operational errors in the database by generating a
    custom exception.
    """

    material_category_model = MaterialCategory

    @classmethod
    def get_material_category(
        cls,
        filters: Dict[str, Any],
    ) -> QuerySet[MaterialCategory]:

        try:
            # fmt: off
            return (
                cls.material_category_model.objects
                .filter(**filters)
                .defer("id", "date_joined")
            )
            # fmt: on
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def create_material_category(cls, data: Dict[str, Any]) -> MaterialCategory:

        try:
            return cls.material_category_model.objects.create(
                is_active=True,
                **data,
            )
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def deactivate_material_category(
        cls,
        instance: MaterialCategory,
    ) -> MaterialCategory:

        try:
            instance.is_active = False
            instance.save()

            return instance
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()


class StaticInfoRepository(
    IStaticInfoRepository,
    MaterialCategoryRepository,
    CuttingTechniqueRepository,
    MaterialRepository,
    ThicknessMaterialRepository,
):
    """
    A repository class that implements various repositories for managing static
    information entities in the database.
    """

    @classmethod
    def exists(cls, data_type: str, data: Dict[str, Any]) -> bool:

        model_mapping = {
            "material_category": cls.material_category_model,
            "cut": cls.cutting_technique_model,
            "material": cls.material_model,
        }

        try:
            model: Model = model_mapping.get(data_type, None)

            if model is None:
                raise ValueError(f"Invalid data type: {data_type}")

            return model.objects.filter(**data).exists()
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def change_status(cls, instance: Model, value: bool) -> None:

        try:
            instance.is_active = value
            instance.save()
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()


class UsesCutsRepository(IUsesCutsRepository):
    """
    Provides an abstraction of the database operations or queries related to
    the uses of cutting techniques in different materials.
    """

    model = UsesCuts

    @classmethod
    def get(cls, cut_code: str = None, all: bool = False) -> QuerySet[UsesCuts]:

        try:
            if all:
                return cls.model.objects.all()

            # fmt: off
            return (
                cls.model.objects
                .filter(cut__code=cut_code)
                .select_related("cut")
            )
            # fmt: on
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def create(cls, cut: CuttingTechnique, num_uses: int) -> None:

        try:
            cls.model.objects.create(cut=cut, number_uses=num_uses)
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()

    @classmethod
    def update(cls, num_uses: int, instance: UsesCuts) -> str:

        status = NO_CHANGE_CUTTING

        try:
            new_uses = instance.number_uses + num_uses

            if instance.number_uses == 0 and new_uses > 0:
                status = REACTIVATE_CUTTING
            elif new_uses == 0:
                instance.cut.is_active = False
                instance.cut.save()
                status = DEACTIVATE_CUTTING

            instance.number_uses = new_uses
            instance.save()

            return status
        except OperationalError:
            # In the future, a retry system will be implemented when the database is
            # suddenly unavailable.
            raise DatabaseConnectionAPIError()
