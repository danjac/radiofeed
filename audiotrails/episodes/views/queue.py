import http

from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST
from turbo_response import Action, TurboStream
from turbo_response.decorators import turbo_stream_response

from ..models import QueueItem
from . import get_episode_or_404


@login_required
def index(request):
    return TemplateResponse(
        request,
        "episodes/queue.html",
        {
            "queue_items": QueueItem.objects.filter(user=request.user)
            .select_related("episode", "episode__podcast")
            .order_by("position")
        },
    )


@require_POST
@turbo_stream_response
def add_to_queue(request, episode_id):

    episode = get_episode_or_404(request, episode_id, with_podcast=True)

    if request.user.is_anonymous:
        return redirect_to_login(episode.get_absolute_url())

    streams = [
        render_queue_toggle(request, episode, is_queued=True),
    ]

    items = QueueItem.objects.filter(user=request.user)

    try:
        new_item = QueueItem.objects.create(
            user=request.user,
            episode=episode,
            position=(items.aggregate(Max("position"))["position__max"] or 0) + 1,
        )
    except IntegrityError:
        return streams

    return streams + [
        TurboStream("queue")
        .action(Action.UPDATE if items.count() == 1 else Action.APPEND)
        .template(
            "episodes/_queue_item.html",
            {
                "episode": episode,
                "item": new_item,
                "dom_id": episode.dom.queue,
            },
        )
        .render(request=request)
    ]


@require_POST
@turbo_stream_response
def remove_from_queue(request, episode_id):
    episode = get_episode_or_404(request, episode_id)

    if request.user.is_anonymous:
        return redirect_to_login(episode.get_absolute_url())

    return [
        render_queue_toggle(request, episode, is_queued=False),
        render_remove_from_queue(request, episode),
    ]


@require_POST
def move_queue_items(request):

    if request.user.is_anonymous:
        return HttpResponseForbidden("You must be logged in")

    qs = QueueItem.objects.filter(user=request.user)
    items = qs.in_bulk()
    for_update = []

    try:
        for position, item_id in enumerate(request.POST.getlist("items"), 1):
            if item := items[int(item_id)]:
                item.position = position
                for_update.append(item)
    except (KeyError, ValueError):
        return HttpResponseBadRequest("Invalid payload")

    qs.bulk_update(for_update, ["position"])
    return HttpResponse(status=http.HTTPStatus.NO_CONTENT)


def render_queue_toggle(request, episode, is_queued):
    return (
        TurboStream(episode.dom.queue_toggle)
        .replace.template(
            "episodes/_queue_toggle.html",
            {"episode": episode, "is_queued": is_queued},
        )
        .render(request=request)
    )


def render_remove_from_queue(request, episode):
    qs = QueueItem.objects.filter(user=request.user)
    qs.filter(episode=episode).delete()

    if not qs.exists():
        return TurboStream("queue").update.render(
            "You have no more episodes in your Play Queue"
        )
    return TurboStream(episode.dom.queue).remove.render()