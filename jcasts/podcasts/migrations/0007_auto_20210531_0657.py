# Generated by Django 3.2.3 on 2021-05-31 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0006_update_search_vector_trigger"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="podcast",
            name="cover_image",
        ),
        migrations.AddField(
            model_name="podcast",
            name="cover_url",
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]