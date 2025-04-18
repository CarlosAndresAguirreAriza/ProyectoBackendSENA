# Generated by Django 5.1.3 on 2025-02-10 21:26

import django.db.models.deletion
import phonenumber_field.modelfields
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "users",
            "0003_rename_users_user_uuid_5a965c_idx_users_users_uuid_262421_idx_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminRole",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        db_column="uuid",
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        db_column="first_name", default="No tiene", max_length=25
                    ),
                ),
                (
                    "last_name",
                    models.CharField(db_column="last_name", max_length=25),
                ),
            ],
            options={
                "verbose_name": "Admin role",
                "verbose_name_plural": "Admins role",
                "db_table": "users.admin_role",
            },
        ),
        migrations.CreateModel(
            name="CompanyRole",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        db_column="uuid",
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "name",
                    models.CharField(db_column="name", max_length=40, unique=True),
                ),
                (
                    "ruc",
                    models.CharField(
                        blank=True,
                        db_column="ruc",
                        db_index=True,
                        max_length=13,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        db_column="phone_number",
                        db_index=True,
                        max_length=19,
                        null=True,
                        region=None,
                        unique=True,
                    ),
                ),
                ("address", models.CharField(db_column="address", max_length=40)),
            ],
            options={
                "verbose_name": "Company role",
                "verbose_name_plural": "Companies role",
                "db_table": "users.company_role",
            },
        ),
        migrations.CreateModel(
            name="NaturalPersonRole",
            fields=[
                (
                    "uuid",
                    models.UUIDField(
                        db_column="uuid",
                        default=uuid.uuid4,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        db_column="first_name", default="No tiene", max_length=25
                    ),
                ),
                (
                    "last_name",
                    models.CharField(db_column="last_name", max_length=25),
                ),
                (
                    "cc",
                    models.CharField(
                        blank=True,
                        db_column="cc",
                        db_index=True,
                        max_length=10,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True,
                        db_column="phone_number",
                        db_index=True,
                        max_length=19,
                        null=True,
                        region=None,
                        unique=True,
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True, db_column="address", max_length=40, null=True
                    ),
                ),
            ],
            options={
                "verbose_name": "Natural person role",
                "verbose_name_plural": "Natural persons role",
                "db_table": "users.natural_person_role",
            },
        ),
        migrations.DeleteModel(
            name="AdminRoleData",
        ),
        migrations.DeleteModel(
            name="CompanyRoleData",
        ),
        migrations.DeleteModel(
            name="NaturalPersonRoleData",
        ),
        migrations.RemoveField(
            model_name="user",
            name="content_type",
        ),
        migrations.RemoveField(
            model_name="user",
            name="role_data_uuid",
        ),
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(db_column="role", max_length=60, null=True),
        ),
        migrations.AddField(
            model_name="adminrole",
            name="base_data",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="adminrole",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="companyrole",
            name="base_data",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="companyrole",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="naturalpersonrole",
            name="base_data",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="naturalpersonrole",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
