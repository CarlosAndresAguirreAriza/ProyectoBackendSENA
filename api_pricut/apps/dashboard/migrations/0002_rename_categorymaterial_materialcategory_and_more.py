# Generated by Django 5.1.3 on 2025-01-22 15:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="CategoryMaterial",
            new_name="MaterialCategory",
        ),
        migrations.AlterModelOptions(
            name="materialcategory",
            options={
                "verbose_name": "Material category",
                "verbose_name_plural": "Material categories",
            },
        ),
        migrations.AlterField(
            model_name="thicknessmaterial",
            name="material",
            field=models.ForeignKey(
                db_column="material",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="thicknesses",
                to="dashboard.material",
            ),
        ),
        migrations.AlterModelTable(
            name="materialcategory",
            table="dashboard.material_categories",
        ),
    ]
