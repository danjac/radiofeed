from __future__ import annotations

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

from jcasts.episodes.models import Episode, QueueItem
from jcasts.episodes.views import get_episode_or_404
from jcasts.shared.decorators import ajax_login_required
from jcasts.shared.response import HttpResponseNoContent, with_hx_trigger


@require_POST
@ajax_login_required
def start_player(request: HttpRequest, episode_id: int) -> HttpResponse:
    episode = get_episode_or_404(request, episode_id, with_podcast=True)
    request.player.start_episode(episode)
    return render_player(request, next_episode=episode)


@require_POST
@ajax_login_required
def close_player(request: HttpRequest) -> HttpResponse:
    if log := request.player.stop_episode():
        current_episode = log.episode
    else:
        current_episode = None
    return render_player(request, current_episode=current_episode)


@require_POST
@ajax_login_required
def mark_complete(request: HttpRequest) -> HttpResponse:
    """Marks current episode complete, starts next episode in queue
    or closes player if queue empty."""

    if log := request.player.stop_episode(mark_completed=True):
        current_episode = log.episode
    else:
        current_episode = None

    if request.user.autoplay and (
        next_item := (
            QueueItem.objects.filter(user=request.user)
            .with_current_time(request.user)
            .select_related("episode", "episode__podcast")
            .order_by("position")
            .first()
        )
    ):
        next_episode = next_item.episode
        request.player.start_episode(next_episode)
    else:
        next_episode = None

    return render_player(
        request,
        next_episode=next_episode,
        current_episode=current_episode,
    )


@require_POST
@ajax_login_required
def player_time_update(request: HttpRequest) -> HttpResponse:
    """Update current play time of episode"""
    try:
        request.player.update_current_time(float(request.POST["current_time"]))
        return HttpResponseNoContent()
    except (KeyError, ValueError):
        return HttpResponseBadRequest("missing or invalid data")


def render_player(
    request: HttpRequest,
    current_episode: Episode | None = None,
    next_episode: Episode | None = None,
) -> HttpResponse:

    response = TemplateResponse(request, "_player.html", {"unlock": True})

    if next_episode:
        response = with_hx_trigger(
            response,
            {
                "remove-queue-item": next_episode.id,
            },
        )

    return response
