# Generated by Django 3.1.6 on 2021-02-10 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0013_auto_20210210_1530"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcast",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
