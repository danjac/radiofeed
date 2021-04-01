import dataclasses
import json

from typing import Optional

import requests

from django.core.cache import cache
from django.utils.encoding import force_str

from .models import Category, Podcast

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


class Timeout(requests.exceptions.Timeout):
    pass


class Invalid(requests.RequestException):
    pass


@dataclasses.dataclass
class SearchResult:
    rss: str
    itunes: str
    title: str
    image: str
    podcast: Optional[Podcast] = None

    def as_dict(self):
        return {
            "rss": self.rss,
            "title": self.title,
            "itunes": self.itunes,
            "image": self.image,
            "podcast": self.podcast,
        }

    def as_json(self):
        return json.dumps(self.as_dict())


def fetch_itunes_genre(genre_id, num_results=20):
    """Fetch top rated results for genre"""
    return _get_or_create_podcasts(
        _get_search_results(
            {
                "term": "podcast",
                "limit": num_results,
                "genreId": genre_id,
            },
            cache_key=f"itunes:genre:{genre_id}",
        )
    )


def search_itunes(search_term, num_results=12):
    """Does a search query on the iTunes API."""

    return _get_or_create_podcasts(
        _get_search_results(
            {
                "media": "podcast",
                "limit": num_results,
                "term": force_str(search_term),
            },
            cache_key=f"itunes:search:{search_term}",
        )
    )


def crawl_itunes(limit):
    categories = Category.objects.filter(itunes_genre_id__isnull=False).order_by("name")
    new_podcasts = 0

    for category in categories:
        podcasts = []

        try:
            results, podcasts = fetch_itunes_genre(
                category.itunes_genre_id, num_results=limit
            )
        except (Invalid, Timeout):
            continue

        new_podcasts += len(podcasts)
    return new_podcasts


def _get_or_create_podcasts(results):
    """Looks up podcast associated with result. Optionally adds new podcasts if not found"""
    podcasts = Podcast.objects.filter(itunes__in=[r.itunes for r in results]).in_bulk(
        field_name="itunes"
    )
    new_podcasts = []
    for result in results:
        result.podcast = podcasts.get(result.itunes, None)
        if result.podcast is None:
            new_podcasts.append(
                Podcast(title=result.title, rss=result.rss, itunes=result.itunes)
            )

    if new_podcasts:
        Podcast.objects.bulk_create(new_podcasts, ignore_conflicts=True)

    return results, new_podcasts


def _get_search_results(
    params,
    cache_key,
    cache_timeout=86400,
    requests_timeout=3,
):

    results = cache.get(cache_key)
    if results is None:
        try:
            response = requests.get(
                ITUNES_SEARCH_URL,
                params,
                timeout=requests_timeout,
                verify=True,
            )
            response.raise_for_status()
            results = response.json()["results"]
            cache.set(cache_key, results, timeout=cache_timeout)
        except KeyError as e:
            raise Invalid from e
        except requests.exceptions.Timeout as e:
            raise Timeout from e
        except requests.RequestException as e:
            raise Invalid from e

    return [
        SearchResult(
            item["feedUrl"],
            item["trackViewUrl"],
            item["collectionName"],
            item["artworkUrl600"],
        )
        for item in results
        if "feedUrl" in item
    ]