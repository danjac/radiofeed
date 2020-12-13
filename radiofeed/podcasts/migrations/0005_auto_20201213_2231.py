# Generated by Django 3.1.3 on 2020-12-13 22:31

# Django
import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("podcasts", "0004_auto_20201213_1448"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="podcast", name="podcasts_po_title_b6422d_idx",
        ),
        migrations.RemoveIndex(
            model_name="podcast", name="podcasts_po_title_f62b0b_idx",
        ),
        migrations.AddField(
            model_name="podcast",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(
                editable=False, null=True
            ),
        ),
        migrations.AddIndex(
            model_name="podcast",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["search_vector"], name="podcasts_po_search__4c951f_gin"
            ),
        ),
    ]
