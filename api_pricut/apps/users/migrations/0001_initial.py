# Generated by Django 5.1.3 on 2024-11-24 21:53

import apps.users.models
import django.db.models.deletion
import phonenumber_field.modelfields
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="CompanyRoleData",
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
                "verbose_name": "Company role data",
                "verbose_name_plural": "Companies role data",
                "db_table": "users.company_role_data",
            },
        ),
        migrations.CreateModel(
            name="NaturalPersonRoleData",
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
                "verbose_name": "Natural person role data",
                "verbose_name_plural": "Natural persons role data",
                "db_table": "users.natural_person_role_data",
            },
        ),
        migrations.CreateModel(
            name="User",
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
                    "email",
                    models.EmailField(
                        db_column="email",
                        db_index=True,
                        max_length=40,
                        unique=True,
                    ),
                ),
                (
                    "password",
                    models.CharField(db_column="password", max_length=128),
                ),
                (
                    "role_data_uuid",
                    models.UUIDField(
                        blank=True, db_column="role_data_uuid", null=True
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(db_column="is_staff", default=False),
                ),
                (
                    "is_superuser",
                    models.BooleanField(db_column="is_superuser", default=False),
                ),
                (
                    "is_active",
                    models.BooleanField(db_column="is_active", default=False),
                ),
                (
                    "is_deleted",
                    models.BooleanField(db_column="is_deleted", default=False),
                ),
                (
                    "deleted_at",
                    models.DateTimeField(
                        blank=True, db_column="deleted_at", null=True
                    ),
                ),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, db_column="last_login", null=True
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        auto_now_add=True, db_column="date_joined"
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        db_column="content_type",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "User",
                "verbose_name_plural": "Users",
                "db_table": "users.user",
                "indexes": [
                    models.Index(
                        fields=["uuid", "is_active"],
                        name="users.user_uuid_5a965c_idx",
                    ),
                    models.Index(
                        fields=["email", "is_active"],
                        name="users.user_email_054a49_idx",
                    ),
                ],
            },
            managers=[
                ("objects", apps.users.models.UserManager()),
            ],
        ),
    ]
