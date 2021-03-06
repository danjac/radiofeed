# Generated by Django 3.2.5 on 2021-07-10 07:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0013_auto_20210613_0727"),
    ]

    operations = [
        migrations.AlterField(
            model_name="podcast",
            name="cover_url",
            field=models.URLField(blank=True, max_length=2083, null=True),
        ),
        migrations.AlterField(
            model_name="podcast",
            name="itunes",
            field=models.URLField(blank=True, max_length=2083, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="podcast",
            name="link",
            field=models.URLField(blank=True, max_length=2083, null=True),
        ),
    ]
