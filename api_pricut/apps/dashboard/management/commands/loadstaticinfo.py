from apps.dashboard.infrastructure.repositories import (
    StaticInfoRepository,
    UsesCutsRepository,
)
from settings.environments.base import BASE_DIR
from django.core.management.base import BaseCommand
from typing import List, Dict
import json


class Command(BaseCommand):
    """
    Load the static information into the database. This command is used to
    populate the database with the necessary information to start the application.
    """

    __static_info_repository = StaticInfoRepository
    __uses_cuts_repository = UsesCutsRepository

    def handle(self, *args, **kwargs):
        """Load the static information into the database."""

        self._load_category_meterials()
        self.stdout.write(msg="")
        self._load_cutting_techniques()
        self.stdout.write(msg="")
        self._load_materials()

        self.stdout.write(
            msg=self.style.SUCCESS("\nStatic information loaded successfully.\n")
        )

    def _read_fixture(self, path: str) -> List[Dict]:
        """Reads the fixture file and returns the data as a list of dictionaries."""

        with open(path, "r") as file:
            json_string = json.load(file)

        return json_string

    def _load_category_meterials(self) -> None:
        """
        Loads the category materials from the fixtures and creates them in the
        database. If the category material already exists, it will be skipped.
        """

        path = f"{BASE_DIR}/apps/dashboard/fixtures/category_materials.json"
        category_materials = self._read_fixture(path=path)

        # Extract the names of the materials to display them in the console
        material_names = [
            category_material["name"] for category_material in category_materials
        ]
        material_list = ", ".join(material_names)
        self.stdout.write(
            msg=self.style.MIGRATE_HEADING("Loading Category Materials:\n")
            + f"   {self.style.MIGRATE_LABEL('Categories:')} {material_list}\n"
            + self.style.MIGRATE_HEADING("Creating the data:")
        )

        # Create the category materials in the database
        for category_material in category_materials:
            code = category_material["code"]
            exists = self.__static_info_repository.exists(
                data_type="material_category",
                data={"code": code},
            )

            if not exists:
                self.__static_info_repository.create_material_category(
                    data=category_material
                )
                self.stdout.write(
                    msg=f"   Creating category.{code}... "
                    + self.style.SUCCESS("OK")
                )
            else:
                self.stdout.write(
                    msg=f"    Creating category.{code}... Already exists: "
                    + self.style.WARNING("SKIPPED")
                )

    def _load_cutting_techniques(self) -> None:
        """
        Loads the cutting techniques from the fixtures and creates them in the
        database. If the cutting technique already exists, it will be skipped.
        """

        path = f"{BASE_DIR}/apps/dashboard/fixtures/cutting_techniques.json"
        cutting_techniques = self._read_fixture(path=path)

        # Extract the names of the techniques to display them in the console
        technique_names = [technique["name"] for technique in cutting_techniques]
        technique_list = ", ".join(technique_names)
        self.stdout.write(
            msg=self.style.MIGRATE_HEADING("Loading cutting techniques:\n")
            + f"   {self.style.MIGRATE_LABEL('Techniques:')} {technique_list}\n"
            + self.style.MIGRATE_HEADING("Creating the data:")
        )

        # Create the cutting techniques in the database
        for technique in cutting_techniques:
            code = technique["code"]
            exists = self.__static_info_repository.exists(
                data={"code": code},
                data_type="cut",
            )

            if not exists:
                obj = self.__static_info_repository.create_cut(data=technique)
                obj.is_active = True
                obj.save()

                self.stdout.write(
                    msg=f"   Creating technique.{code}... "
                    + self.style.SUCCESS("OK")
                )
            else:
                self.stdout.write(
                    msg=f"    Creating technique.{code}... Already exists: "
                    + self.style.WARNING("SKIPPED")
                )

    def _load_materials(self) -> None:
        """
        Loads the materials from the fixtures and creates them in the database.
        If the material already exists, it will be skipped.
        """

        path = f"{BASE_DIR}/apps/dashboard/fixtures/materials.json"
        materials = self._read_fixture(path=path)

        # Extract the names of the materials to display them in the console
        material_names = [material["name"] for material in materials]
        material_list = ", ".join(material_names)
        self.stdout.write(
            msg=self.style.MIGRATE_HEADING("Loading materials:\n")
            + f"   {self.style.MIGRATE_LABEL('Materials:')} {material_list}\n"
            + self.style.MIGRATE_HEADING("Creating the data:")
        )

        # Create a materials in the database
        counter_uses_cuts = {}

        for material in materials:
            code = material["code"]
            thickness_cutting = material.pop("thickness_cutting")
            exists = self.__static_info_repository.exists(
                data_type="material",
                data={"code": code},
            )

            if exists:
                self.stdout.write(
                    msg=f"    Creating material.{code}... Already exists: "
                    + self.style.WARNING("SKIPPED")
                )
                continue

            category_code = material.pop("category_code")
            category = self.__static_info_repository.get_material_category(
                filters={"code": category_code}
            ).first()
            material = self.__static_info_repository.create_material(
                category=category,
                data=material,
            )
            self.__static_info_repository.create_thicknesses(
                data=thickness_cutting,
                material=material,
            )
            self.stdout.write(
                msg=f"   Creating material.{code}... " + self.style.SUCCESS("OK")
            )

            # The number of uses of the cutting techniques available in each
            # material is counted.
            for data in thickness_cutting:
                compatibility_cut = data["compatibility_cut"]

                for cut_code, compatibility in compatibility_cut.items():
                    if not counter_uses_cuts.get(cut_code, None):
                        counter_uses_cuts[cut_code] = 0
                    if compatibility:
                        counter_uses_cuts[cut_code] += 1

        for cut_code, uses in counter_uses_cuts.items():
            cut = self.__static_info_repository.get_cut(
                filters={"code": cut_code}
            ).first()
            self.__uses_cuts_repository.create(cut=cut, num_uses=uses)
