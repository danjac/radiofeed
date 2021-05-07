from django.urls import path

from .views import (
    episode_detail,
    favorites,
    history,
    index,
    player,
    preview,
    queue,
    search_episodes,
)

app_name = "episodes"


urlpatterns = [
    path("", index, name="index"),
    path("featured/", index, name="featured", kwargs={"featured": True}),
    path("search/episodes/", search_episodes, name="search_episodes"),
    path(
        "episodes/preview/<int:episode_id>/",
        preview,
        name="episode_preview",
    ),
    path(
        "episodes/<int:episode_id>/<slug:slug>/",
        episode_detail,
        name="episode_detail",
    ),
    path(
        "player/<int:episode_id>/~start/",
        player.start_player,
        name="start_player",
    ),
    path(
        "player/~close/",
        player.close_player,
        name="close_player",
    ),
    path(
        "player/~next/",
        player.play_next_episode,
        name="play_next_episode",
    ),
    path(
        "player/~timeupdate/",
        player.player_time_update,
        name="player_time_update",
    ),
    path("history/", history.index, name="history"),
    path(
        "history/<int:episode_id>/~remove/",
        history.remove_audio_log,
        name="remove_audio_log",
    ),
    path("favorites/", favorites.index, name="favorites"),
    path(
        "favorites/<int:episode_id>/~add/",
        favorites.add_favorite,
        name="add_favorite",
    ),
    path(
        "favorites/<int:episode_id>/~remove/",
        favorites.remove_favorite,
        name="remove_favorite",
    ),
    path("queue/", queue.index, name="queue"),
    path("queue/~move/", queue.move_queue_items, name="move_queue_items"),
    path("queue/<int:episode_id>/~add/", queue.add_to_queue, name="add_to_queue"),
    path(
        "queue/<int:episode_id>/~remove/",
        queue.remove_from_queue,
        name="remove_from_queue",
    ),
]
