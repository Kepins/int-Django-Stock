# Generated by Django 4.2.4 on 2023-08-10 15:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0006_alter_stock_last_update_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stocktimeseries",
            name="stock",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="series", to="application.stock"
            ),
        ),
        migrations.CreateModel(
            name="Follow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="application.stock")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="follows",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "stock")},
            },
        ),
    ]
