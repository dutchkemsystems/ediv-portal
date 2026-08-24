# Generated manually for Access Database models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("data_import_export", "0001_initial_import_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccessDatabase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("file", models.FileField(upload_to="access_databases/")),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("UPLOADED", "Uploaded"),
                            ("PROCESSING", "Processing"),
                            ("READY", "Ready"),
                            ("ERROR", "Error"),
                        ],
                        default="UPLOADED",
                        max_length=20,
                    ),
                ),
                ("total_tables", models.IntegerField(default=0)),
                ("total_records", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "uploaded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="access_databases",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AccessTableData",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("table_name", models.CharField(max_length=200)),
                ("row_index", models.IntegerField()),
                ("data", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "database",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="table_data",
                        to="data_import_export.accessdatabase",
                    ),
                ),
            ],
            options={
                "ordering": ["table_name", "row_index"],
                "unique_together": {("database", "table_name", "row_index")},
            },
        ),
        migrations.CreateModel(
            name="AccessPrivilege",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "privilege_level",
                    models.CharField(
                        choices=[
                            ("VIEW", "View"),
                            ("EDIT", "Edit"),
                            ("DELETE", "Delete"),
                            ("ADMIN", "Admin"),
                        ],
                        default="VIEW",
                        max_length=10,
                    ),
                ),
                ("granted_at", models.DateTimeField(auto_now_add=True)),
                (
                    "database",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="privileges",
                        to="data_import_export.accessdatabase",
                    ),
                ),
                (
                    "granted_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="granted_access_privileges",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="access_privileges",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-granted_at"],
                "unique_together": {("database", "user")},
            },
        ),
    ]
