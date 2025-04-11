from apps.dashboard.infrastructure import StaticInfoRepository, UsesCutsRepository
from apps.users.domain.constants import (
    NATURAL_PERSON_ROLE,
    COMPANY_ROLE,
    ADMIN_ROLE,
)
from apps.permissions import PERMISSIONS, USER_ROLE_PERMISSIONS
from settings.environments.base import BASE_DIR
from django.contrib.auth.models import Group, Permission
import pytest
import json


@pytest.fixture()
def load_user_groups(db) -> None:
    """Set up data for the whole TestCase."""

    user_roles = [NATURAL_PERSON_ROLE, COMPANY_ROLE, ADMIN_ROLE]

    for role in user_roles:
        # Create the group and assign permissions
        group = Group.objects.create(name=role)

        for perm in USER_ROLE_PERMISSIONS[role]:
            perm_codename = PERMISSIONS[perm].split(".")[-1]
            perm = Permission.objects.get(codename=perm_codename)
            group.permissions.add(perm)


@pytest.fixture()
def load_static_info(db) -> None:
    """Load static information into the database."""

    # Load the category materials
    path = f"{BASE_DIR}/apps/dashboard/fixtures/category_materials.json"

    with open(path, "r") as file:
        category_materials = json.load(file)

    for category_material in category_materials:
        StaticInfoRepository.create_material_category(data=category_material)

    # Load the cutting techniques
    path = f"{BASE_DIR}/apps/dashboard/fixtures/cutting_techniques.json"

    with open(path, "r") as file:
        cutting_techniques = json.load(file)

    for technique in cutting_techniques:
        obj = StaticInfoRepository.create_cut(data=technique)
        obj.is_active = True
        obj.save()

    # Load the materials
    path = f"{BASE_DIR}/apps/dashboard/fixtures/materials.json"

    with open(path, "r") as file:
        materials = json.load(file)

    counter_uses_cuts = {}

    for material_data in materials:
        thickness_cutting = material_data.pop("thickness_cutting")
        category_code = material_data.pop("category_code")
        category = StaticInfoRepository.get_material_category(
            filters={"code": category_code}
        ).first()
        material = StaticInfoRepository.create_material(
            data=material_data,
            category=category,
        )
        StaticInfoRepository.create_thicknesses(
            material=material,
            data=thickness_cutting,
        )

        # The number of uses of the cutting techniques available in each material is counted.
        for data in thickness_cutting:
            compatibility_cut = data["compatibility_cut"]

            for cut_code, compatibility in compatibility_cut.items():
                if not counter_uses_cuts.get(cut_code, None):
                    counter_uses_cuts[cut_code] = 0
                if compatibility:
                    counter_uses_cuts[cut_code] += 1

    for cut_code, uses in counter_uses_cuts.items():
        cut = StaticInfoRepository.get_cut(
            filters={"code": cut_code},
            section="base_info",
        ).first()
        UsesCutsRepository.create(cut=cut, num_uses=uses)
