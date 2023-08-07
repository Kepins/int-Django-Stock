# Generated by Django 4.2.4 on 2023-08-07 09:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("application", "0002_alter_user_password"),
    ]

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Currency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name="Stock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=250)),
                ("symbol", models.CharField(max_length=40)),
                ("exchange_name", models.CharField(max_length=40)),
                ("type_of_stock", models.CharField(choices=[("Common Stock", "Common Stock")], max_length=100)),
                ("last_update_date", models.DateTimeField()),
                ("country", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="application.country")),
                (
                    "currency",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="application.currency"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="StockTimeSeries",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("open", models.FloatField()),
                ("close", models.FloatField()),
                ("high", models.FloatField()),
                ("low", models.FloatField()),
                ("volume", models.IntegerField()),
                ("recorded_date", models.DateTimeField()),
                ("stock", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="application.stock")),
            ],
        ),
    ]
