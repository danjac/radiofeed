# Generated by Django 3.2.4 on 2021-06-12 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0011_set_modified_to_null"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="exception",
            field=models.TextField(blank=True),
        ),
    ]
