# Generated by Django 3.1.7 on 2021-03-10 10:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("podcasts", "0018_remove_podcast_cover_image_etag"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Subscription",
            new_name="Follow",
        ),
        migrations.RemoveIndex(
            model_name="follow",
            name="podcasts_su_created_55323d_idx",
        ),
        migrations.AddIndex(
            model_name="follow",
            index=models.Index(
                fields=["-created"], name="podcasts_fo_created_0c8c22_idx"
            ),
        ),
    ]