from __future__ import annotations

import collections
import datetime
import logging
import operator
import statistics

from typing import Generator

import pandas

from django.db import transaction
from django.db.models import QuerySet
from django.db.models.functions import Lower
from django.utils import timezone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from jcasts.podcasts.models import Category, Podcast, Recommendation
from jcasts.podcasts.text_parser import get_stopwords

logger = logging.getLogger(__name__)


NUM_MATCHES: int = 12
NUM_RECENT_EPISODES: int = 6
MAX_PUB_DAYS: int = 90


def recommend() -> None:

    podcasts = get_podcast_queryset()

    Recommendation.objects.bulk_delete()

    categories = Category.objects.order_by("name")

    # separate by language, so we don't get false matches
    languages = [
        lang
        for lang in podcasts.values_list(Lower("language"), flat=True).distinct()
        if lang
    ]

    for language in languages:
        create_recommendations_for_language(podcasts, categories, language)


def get_podcast_queryset() -> QuerySet:
    return Podcast.objects.filter(
        pub_date__gt=timezone.now() - datetime.timedelta(days=MAX_PUB_DAYS)
    ).exclude(extracted_text="")


def create_recommendations_for_language(
    podcasts: QuerySet,
    categories: QuerySet,
    language: str,
) -> None:
    logger.info("Recommendations for %s", language)

    matches = build_matches_dict(
        podcasts,
        categories,
        language,
    )

    with transaction.atomic():

        if matches:
            logger.info("Inserting %d recommendations:%s", len(matches), language)
            Recommendation.objects.bulk_create(
                recommendations_from_matches(matches),
                batch_size=100,
                ignore_conflicts=True,
            )


def build_matches_dict(
    podcasts: QuerySet,
    categories: QuerySet,
    language: str,
) -> dict[tuple[int, int], list]:

    matches = collections.defaultdict(list)
    podcasts = podcasts.filter(language__iexact=language)

    # individual graded category matches
    for category in categories:
        logger.info("Recommendations for %s:%s", language, category)
        for (podcast_id, recommended_id, similarity,) in find_similarities_for_podcasts(
            podcasts.filter(categories=category), language
        ):
            matches[(podcast_id, recommended_id)].append(similarity)

    return matches


def recommendations_from_matches(matches) -> Generator[Recommendation, None, None]:
    for (podcast_id, recommended_id), values in matches.items():
        frequency = len(values)
        similarity = statistics.median(values)

        yield Recommendation(
            podcast_id=podcast_id,
            recommended_id=recommended_id,
            similarity=similarity,
            frequency=frequency,
        )


def find_similarities_for_podcasts(
    podcasts: QuerySet, language: str
) -> Generator[tuple[int, int, float], None, None]:

    if not podcasts.exists():  # pragma: no cover
        return

    for podcast_id, recommended in find_similarities(podcasts, language):
        for recommended_id, similarity in recommended:
            similarity = round(similarity, 2)
            if similarity > 0:
                yield podcast_id, recommended_id, similarity


def find_similarities(
    podcasts: QuerySet, language: str
) -> Generator[tuple[int, list[tuple[int, float]]], None, None]:
    """Given a queryset, will yield tuples of
    (id, (similar_1, similar_2, ...)) based on text content.
    """

    df = pandas.DataFrame(podcasts.values("id", "extracted_text"))

    df.drop_duplicates(inplace=True)

    vec = TfidfVectorizer(
        stop_words=get_stopwords(language),
        max_features=3000,
        ngram_range=(1, 2),
    )

    try:
        count_matrix = vec.fit_transform(df["extracted_text"])
    except ValueError:  # pragma: no cover
        return

    cosine_sim = cosine_similarity(count_matrix)

    for index in df.index:
        try:
            yield find_similarity(
                df, similar=cosine_sim[index], current_id=df.loc[index, "id"]
            )
        except IndexError:  # pragma: no cover
            pass


def find_similarity(
    df: pandas.DataFrame, similar: list[int], current_id: int
) -> tuple[int, list[tuple[int, float]]]:

    sorted_similar = sorted(
        list(enumerate(similar)), key=operator.itemgetter(1), reverse=True
    )[:NUM_MATCHES]

    matches: list[tuple[int, float]] = [
        (df.loc[row, "id"], similarity)
        for row, similarity in sorted_similar
        if df.loc[row, "id"] != current_id
    ]
    return (current_id, matches)
