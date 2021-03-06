from __future__ import annotations

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.http import require_safe

from jcasts.episodes.models import Episode, QueueItem
from jcasts.podcasts.models import Podcast
from jcasts.shared.pagination import render_paginated_response
from jcasts.shared.typedefs import ContextDict


@require_safe
def index(request: HttpRequest, featured: bool = False) -> HttpResponse:

    follows = (
        set(request.user.follow_set.values_list("podcast", flat=True))
        if request.user.is_authenticated
        else set()
    )

    podcast_ids = (
        set(Podcast.objects.filter(promoted=True).values_list("pk", flat=True))
        if featured or not follows
        else follows
    )

    episodes = (
        Episode.objects.select_related("podcast")
        .filter(podcast__in=podcast_ids)
        .order_by("-pub_date")
    )

    return render_episode_list_response(
        request,
        episodes,
        "episodes/index.html",
        {
            "featured": featured,
            "has_follows": bool(follows),
            "search_url": reverse("episodes:search_episodes"),
        },
        cached=featured or request.user.is_anonymous,
    )


@require_safe
def search_episodes(request: HttpRequest) -> HttpResponse:

    if not request.search:
        return redirect("episodes:index")

    episodes = (
        Episode.objects.select_related("podcast")
        .search(request.search)
        .order_by("-rank", "-pub_date")
    )

    return render_episode_list_response(
        request,
        episodes,
        "episodes/search.html",
        cached=True,
    )


@require_safe
def preview(request: HttpRequest, episode_id: int) -> HttpResponse:

    episode = get_episode_or_404(
        request, episode_id, with_podcast=True, with_current_time=True
    )

    return TemplateResponse(
        request,
        "episodes/_preview.html",
        {
            "episode": episode,
        },
    )


@require_safe
def actions(request: HttpRequest, episode_id: int) -> HttpResponse:

    episode = get_episode_or_404(
        request, episode_id, with_podcast=True, with_current_time=True
    )

    num_queue_items: int = (
        0
        if request.user.is_anonymous or request.player.is_playing(episode)
        else QueueItem.objects.filter(user=request.user).count()
    )

    return TemplateResponse(
        request,
        "episodes/_actions.html",
        {
            "episode": episode,
            "is_favorited": episode.is_favorited(request.user),
            "is_queued": episode.is_queued(request.user),
            "is_playing": request.player.is_playing(episode),
            "is_detail": request.GET.get("detail", False),
            "num_queue_items": num_queue_items,
        },
    )


@require_safe
def episode_detail(
    request: HttpRequest, episode_id: int, slug: str | None = None
) -> HttpResponse:
    episode = get_episode_or_404(
        request, episode_id, with_podcast=True, with_current_time=True
    )

    return TemplateResponse(
        request,
        "episodes/detail.html",
        {
            "episode": episode,
            "og_data": episode.get_opengraph_data(request),
        },
    )


def get_episode_or_404(
    request: HttpRequest,
    episode_id: int,
    *,
    with_podcast: bool = False,
    with_current_time: bool = False,
) -> Episode:
    qs = Episode.objects.all()
    if with_podcast:
        qs = qs.select_related("podcast")
    if with_current_time:
        qs = qs.with_current_time(request.user)
    return get_object_or_404(qs, pk=episode_id)


def render_episode_list_response(
    request: HttpRequest,
    episodes: list[Episode],
    template_name: str,
    extra_context: ContextDict | None = None,
    cached: bool = False,
) -> HttpResponse:
    return render_paginated_response(
        request,
        episodes,
        template_name,
        pagination_template_name="episodes/_episodes_cached.html"
        if cached
        else "episodes/_episodes.html",
        extra_context={
            "cache_timeout": settings.DEFAULT_CACHE_TIMEOUT,
            **(extra_context or {}),
        },
    )
