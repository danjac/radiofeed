# Generated by Django 3.2 on 2021-04-29 09:39

import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [
        ("episodes", "0001_squashed_0010_auto_20201216_1254"),
        ("episodes", "0002_audiolog_completed"),
        ("episodes", "0003_queueitem"),
        ("episodes", "0004_auto_20210206_1207"),
        ("episodes", "0005_auto_20210206_1448"),
        ("episodes", "0006_auto_20210206_2012"),
        ("episodes", "0007_auto_20210210_1515"),
        ("episodes", "0008_auto_20210210_1702"),
        ("episodes", "0009_auto_20210211_1023"),
        ("episodes", "0010_auto_20210219_1521"),
        ("episodes", "0011_auto_20210305_0908"),
        ("episodes", "0012_auto_20210307_0957"),
        ("episodes", "0013_alter_queueitem_id"),
        ("episodes", "0014_auto_20210413_1707"),
        ("episodes", "0015_audiolog_is_playing"),
        ("episodes", "0016_audiolog_playback_rate"),
        ("episodes", "0017_auto_20210417_0805"),
    ]

    initial = True

    dependencies = [
        ("podcasts", "0001_squashed_0006_podcast_search_trigger"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Episode",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("guid", models.TextField()),
                ("pub_date", models.DateTimeField()),
                ("link", models.URLField(blank=True, max_length=500, null=True)),
                ("title", models.TextField(blank=True)),
                ("description", models.TextField(blank=True)),
                ("keywords", models.TextField(blank=True)),
                ("media_url", models.URLField(max_length=500)),
                ("media_type", models.CharField(max_length=20)),
                ("length", models.IntegerField(blank=True, null=True)),
                ("duration", models.CharField(blank=True, max_length=12)),
                ("explicit", models.BooleanField(default=False)),
                (
                    "podcast",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="podcasts.podcast",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["podcast"], name="episodes_ep_podcast_3361d9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["guid"], name="episodes_ep_guid_b00554_idx"),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["-pub_date"], name="episodes_ep_pub_dat_205e36_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["pub_date"], name="episodes_ep_pub_dat_60d1c1_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["title"], name="episodes_ep_title_4a6059_idx"),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(fields=["-title"], name="episodes_ep_title_ce2893_idx"),
        ),
        migrations.AddConstraint(
            model_name="episode",
            constraint=models.UniqueConstraint(
                fields=("podcast", "guid"), name="unique_episode"
            ),
        ),
        migrations.CreateModel(
            name="Bookmark",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="episodes.episode",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="bookmark",
            index=models.Index(
                fields=["-created"], name="episodes_bo_created_d69e08_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="bookmark",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_bookmark"
            ),
        ),
        migrations.AlterField(
            model_name="episode",
            name="duration",
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.RemoveIndex(
            model_name="episode",
            name="episodes_ep_title_4a6059_idx",
        ),
        migrations.RemoveIndex(
            model_name="episode",
            name="episodes_ep_title_ce2893_idx",
        ),
        migrations.AddField(
            model_name="episode",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="episodes_ep_search__466ef4_gin"
            ),
        ),
        migrations.RunSQL(
            sql="\n            CREATE TRIGGER episode_update_search_trigger\n            BEFORE INSERT OR UPDATE OF title, keywords, search_vector\n            ON episodes_episode\n            FOR EACH ROW EXECUTE PROCEDURE\n            tsvector_update_trigger(\n              search_vector, 'pg_catalog.english', title, keywords);\n            UPDATE episodes_episode SET search_vector = NULL;\n            ",
            reverse_sql="\n            DROP TRIGGER IF EXISTS episode_update_search_trigger\n            ON episodes_episode;\n            ",
        ),
        migrations.AlterField(
            model_name="episode",
            name="media_type",
            field=models.CharField(max_length=60),
        ),
        migrations.CreateModel(
            name="History",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("updated", models.DateTimeField()),
                ("completed", models.DateTimeField()),
                ("current_time", models.IntegerField(default=0)),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="episodes.episode",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="history",
            index=models.Index(
                fields=["-updated"], name="episodes_hi_updated_29f4e9_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="history",
            index=models.Index(
                fields=["-completed"], name="episodes_hi_complet_ebe4aa_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="history",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_history"
            ),
        ),
        migrations.AlterField(
            model_name="history",
            name="completed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.RemoveIndex(
            model_name="history",
            name="episodes_hi_complet_ebe4aa_idx",
        ),
        migrations.RemoveField(
            model_name="history",
            name="completed",
        ),
        migrations.RenameModel(
            old_name="History",
            new_name="AudioLog",
        ),
        migrations.RemoveConstraint(
            model_name="audiolog",
            name="uniq_history",
        ),
        migrations.RemoveIndex(
            model_name="audiolog",
            name="episodes_hi_updated_29f4e9_idx",
        ),
        migrations.AddIndex(
            model_name="audiolog",
            index=models.Index(
                fields=["-updated"], name="episodes_au_updated_eb4a9e_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="audiolog",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_audio_log"
            ),
        ),
        migrations.AddField(
            model_name="audiolog",
            name="completed",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="QueueItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                ("position", models.IntegerField(default=0)),
                (
                    "episode",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="episodes.episode",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddIndex(
            model_name="queueitem",
            index=models.Index(
                fields=["position"], name="episodes_qu_positio_58d480_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="queueitem",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_queue_item"
            ),
        ),
        migrations.AddConstraint(
            model_name="queueitem",
            constraint=models.UniqueConstraint(
                fields=("user", "position"), name="uniq_queue_item_position"
            ),
        ),
        migrations.RemoveConstraint(
            model_name="queueitem",
            name="uniq_queue_item_position",
        ),
        migrations.RenameModel(
            old_name="Bookmark",
            new_name="Favorite",
        ),
        migrations.RemoveConstraint(
            model_name="favorite",
            name="uniq_bookmark",
        ),
        migrations.RemoveIndex(
            model_name="favorite",
            name="episodes_bo_created_d69e08_idx",
        ),
        migrations.AddIndex(
            model_name="favorite",
            index=models.Index(
                fields=["-created"], name="episodes_fa_created_edc79e_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="favorite",
            constraint=models.UniqueConstraint(
                fields=("user", "episode"), name="uniq_favorite"
            ),
        ),
        migrations.AlterField(
            model_name="episode",
            name="id",
            field=models.BigAutoField(
                editable=False, primary_key=True, serialize=False
            ),
        ),
        migrations.AlterField(
            model_name="episode",
            name="id",
            field=models.AutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["podcast", "pub_date"], name="episodes_ep_podcast_a7abe0_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="episode",
            index=models.Index(
                fields=["podcast", "-pub_date"], name="episodes_ep_podcast_b9a49e_idx"
            ),
        ),
        migrations.AlterField(
            model_name="audiolog",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="episode",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="favorite",
            name="id",
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="episode",
            name="media_url",
            field=models.URLField(max_length=1000),
        ),
        migrations.AlterField(
            model_name="episode",
            name="length",
            field=models.BigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="queueitem",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="audiolog",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="episode",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
        migrations.AlterField(
            model_name="favorite",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
