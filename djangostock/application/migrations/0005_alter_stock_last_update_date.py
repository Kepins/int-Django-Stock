# Generated by Django 4.2.4 on 2023-08-08 06:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0004_data_country_currency"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stock",
            name="last_update_date",
            field=models.DateTimeField(null=True),
        ),
    ]