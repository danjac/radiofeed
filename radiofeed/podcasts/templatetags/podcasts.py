from typing import Dict, List, Optional

from django import template
from django.db.models import QuerySet
from django.utils import timezone

from ..models import CoverImage, Podcast, Recommendation

register = template.Library()


@register.simple_tag(takes_context=True)
def get_recommendations(context: Dict, limit: int) -> List[Podcast]:
    if (user := context["request"].user).is_anonymous:
        return []
    podcast_ids = dict(
        (podcast_id, podcast_id)
        for podcast_id in Recommendation.objects.for_user(user)
        .select_related("recommended")
        .order_by("-recommended__pub_date", "-similarity")
        .values_list("recommended", flat=True)
        .distinct()[:limit]
    ).keys()
    podcasts = Podcast.objects.in_bulk(podcast_ids)
    return [podcasts[podcast_id] for podcast_id in podcast_ids]


@register.simple_tag
def get_recently_added_podcasts(limit: int) -> QuerySet:
    return get_available_podcasts().order_by("-created", "-pub_date")[:limit]


@register.simple_tag
def get_promoted_podcasts(limit: int) -> QuerySet:
    return get_available_podcasts().filter(promoted=True).order_by("-pub_date")[:limit]


@register.inclusion_tag("podcasts/_cover_image.html")
def cover_image(
    podcast: Podcast,
    lazy: bool = False,
    cover_image: Optional[CoverImage] = None,
    size: str = "16",
    css_class: str = "",
    **attrs,
) -> Dict:
    if not lazy and cover_image is None:
        cover_image = podcast.get_cover_image_thumbnail()

    return {
        "podcast": podcast,
        "lazy": lazy and not (cover_image),
        "cover_image": cover_image,
        "css_class": css_class,
        "img_size": size,
        "attrs": attrs,
    }


def get_available_podcasts() -> QuerySet:
    return Podcast.objects.filter(
        pub_date__isnull=False, cover_image__isnull=False, pub_date__lt=timezone.now()
    ).exclude(cover_image="")
