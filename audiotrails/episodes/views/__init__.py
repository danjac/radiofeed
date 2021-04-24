from django.conf import settings
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from turbo_response import TurboFrame

from audiotrails.podcasts.models import Podcast
from audiotrails.shared.pagination import render_paginated_response

from ..models import AudioLog, Episode


def index(request):

    podcast_ids = []
    listened_ids = []
    show_promotions = False

    if request.user.is_authenticated:
        podcast_ids = list(request.user.follow_set.values_list("podcast", flat=True))
        listened_ids = list(
            AudioLog.objects.filter(user=request.user).values_list("episode", flat=True)
        )

    if not podcast_ids:
        podcast_ids = list(
            Podcast.objects.filter(promoted=True).values_list("pk", flat=True)
        )
        show_promotions = True

    # we want a list of the *latest* episode for each podcast
    latest_episodes = (
        Episode.objects.filter(podcast=OuterRef("pk")).order_by("-pub_date").distinct()
    )

    if listened_ids:
        latest_episodes = latest_episodes.exclude(pk__in=listened_ids)

    episode_ids = (
        Podcast.objects.filter(pk__in=podcast_ids)
        .annotate(latest_episode=Subquery(latest_episodes.values("pk")[:1]))
        .values_list("latest_episode", flat=True)
        .distinct()
    )

    episodes = (
        Episode.objects.select_related("podcast")
        .filter(pk__in=set(episode_ids))
        .order_by("-pub_date")
        .distinct()
    )

    return render_episode_list_response(
        request,
        episodes,
        "episodes/index.html",
        {
            "show_promotions": show_promotions,
            "search_url": reverse("episodes:search_episodes"),
        },
        cached=request.user.is_anonymous,
    )


def search_episodes(request):

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


def preview(request, episode_id):
    episode = get_episode_or_404(
        request, episode_id, with_podcast=True, with_current_time=True
    )

    return (
        TurboFrame(request.turbo.frame)
        .template(
            "episodes/_preview.html",
            get_episode_detail_context(request, episode),
        )
        .response(request)
        if request.turbo.frame
        else redirect(episode.get_absolute_url())
    )


def episode_detail(request, episode_id, slug=None):
    episode = get_episode_or_404(
        request, episode_id, with_podcast=True, with_current_time=True
    )

    return TemplateResponse(
        request,
        "episodes/detail.html",
        get_episode_detail_context(
            request, episode, {"og_data": episode.get_opengraph_data(request)}
        ),
    )


def get_episode_or_404(
    request,
    episode_id,
    *,
    with_podcast=False,
    with_current_time=False,
):
    qs = Episode.objects.all()
    if with_podcast:
        qs = qs.select_related("podcast")
    if with_current_time:
        qs = qs.with_current_time(request.user)
    return get_object_or_404(qs, pk=episode_id)


def get_episode_detail_context(request, episode, extra_context=None):

    return {
        "episode": episode,
        "is_favorited": episode.is_favorited(request.user),
        "is_queued": episode.is_queued(request.user),
        "is_playing": (
            request.session.get("player_episode") == episode.id
            if request.user.is_authenticated
            else False
        ),
        **(extra_context or {}),
    }


def render_episode_list_response(
    request,
    episodes,
    template_name,
    extra_context=None,
    cached=False,
):
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