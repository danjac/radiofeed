# Generated by Django 3.1.7 on 2021-03-03 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0016_auto_20210219_1521"),
    ]

    operations = [
        migrations.AddField(
            model_name="podcast",
            name="cover_image_etag",
            field=models.TextField(blank=True),
        ),
    ]