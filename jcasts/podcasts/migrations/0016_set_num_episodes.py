# Generated by Django 3.2.5 on 2021-07-15 05:21

from django.db import migrations
from django.db.models import Count, OuterRef, Subquery


def set_num_episodes(apps, schema_editor):
    podcast_model = apps.get_model("podcasts.Podcast")
    podcast_model.objects.filter(pub_date__isnull=False).update(
        num_episodes=Subquery(
            podcast_model.objects.filter(pk=OuterRef("id"))
            .annotate(episode_count=Count("episode"))
            .values("episode_count")[:1]
        )
    )


def reset_num_episodes(apps, schema_editor):
    podcast_model = apps.get_model("podcasts.Podcast")
    podcast_model.objects.update(num_episodes=0)


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0015_podcast_num_episodes"),
    ]

    operations = [migrations.RunPython(set_num_episodes, reset_num_episodes)]