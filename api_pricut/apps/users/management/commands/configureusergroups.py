from apps.users.domain.constants import (
    NATURAL_PERSON_ROLE,
    COMPANY_ROLE,
    ADMIN_ROLE,
)
from apps.permissions import PERMISSIONS, USER_ROLE_PERMISSIONS
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission


class Command(BaseCommand):
    """Configure user groups and assign permissions."""

    help = "Create user groups and assign permissions"

    def handle(self, *args, **kwargs):
        """Handle the command, create groups and assign permissions."""

        user_roles = [NATURAL_PERSON_ROLE, COMPANY_ROLE, ADMIN_ROLE]
        group_list = ", ".join(user_roles)
        self.stdout.write(
            msg=self.style.MIGRATE_HEADING(
                "The following user groups will be created:\n"
            )
            + f"   {self.style.MIGRATE_LABEL('Groups')}: {group_list}\n"
        )

        for role in user_roles:
            self.stdout.write(
                msg=self.style.MIGRATE_HEADING(f'Creating group "{role}":')
            )
            group = self.__define_group(name=role)

            for perm in USER_ROLE_PERMISSIONS[role]:
                self.__assign_permissions(perm=PERMISSIONS[perm], group=group)

            self.stdout.write(msg="")

        self.stdout.write(
            msg=self.style.SUCCESS(
                "Permissions successfully assigned to all groups."
            )
        )

    def __define_group(self, name: str) -> Group:
        """Define a group with the given name."""

        group, created = Group.objects.get_or_create(name=name)

        if created:
            self.stdout.write(
                msg=f"{self.style.MIGRATE_LABEL('Creating group')}: {name}"
            )
        else:
            self.stdout.write(
                msg=self.style.WARNING(
                    f'   Group "{name}" already exists, adding missing permissions...\n'
                )
            )

        return group

    def __assign_permissions(self, perm: str, group: Group) -> None:
        """Assign permission to the given group."""

        perm_codename = perm.split(".")[-1]

        try:
            perm_obj = Permission.objects.get(codename=perm_codename)

            if group.permissions.filter(id=perm_obj.id).exists():
                self.stdout.write(
                    msg=f"   Permission {perm}... Already exists: "
                    + self.style.NOTICE("SKIPPED")
                )
            else:
                group.permissions.add(perm_obj)

                self.stdout.write(
                    msg=f"   Added {perm} permission... "
                    + self.style.SUCCESS("OK")
                )
        except Permission.DoesNotExist:
            self.stdout.write(
                msg=f"   Permission {perm}... " + self.style.ERROR("NOT FOUND")
            )
