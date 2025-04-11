# Generated by Django 5.1.3 on 2024-11-28 22:43

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdminRoleData",
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
                "verbose_name": "Admin role data",
                "verbose_name_plural": "Admins role data",
                "db_table": "users.admin_role_data",
            },
        ),
    ]
