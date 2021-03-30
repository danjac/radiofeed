import datetime

import pytest

from django.utils import timezone

from ..factories import AudioLogFactory
from ..models import AudioLog
from ..player import Player

pytestmark = pytest.mark.django_db


class TestPlayer:
    def make_player(self, rf, user=None, session=None):
        req = rf.get("/")
        req.user = user
        req.session = session or {}
        return Player(req)

    def test_empty(self, rf):
        player = Player(rf)
        player = self.make_player(rf)
        assert not player
        assert player.get_episode() is None
        assert player.current_time == 0
        assert player.playback_rate == 1.0

    def test_not_empty(self, rf, user, episode):
        player = self.make_player(
            rf,
            user=user,
            session={
                "player": {
                    "episode": episode.id,
                    "current_time": 1000,
                    "playback_rate": 1.2,
                }
            },
        )
        assert player
        assert player.get_episode() == episode
        assert player.current_time == 1000
        assert player.playback_rate == 1.2

    def test_eject(self, rf, user, episode):
        player = self.make_player(
            rf,
            user=user,
            session={
                "player": {
                    "episode": episode.id,
                    "current_time": 1000,
                    "playback_rate": 1.2,
                }
            },
        )

        assert player.current_time == 1000
        assert player.playback_rate == 1.2
        current_episode = player.eject()

        assert current_episode == episode

        assert not player
        assert player.current_time == 0
        assert player.playback_rate == 1.0

    def test_eject_and_mark_completed(self, rf, user, episode):
        player = self.make_player(
            rf,
            user=user,
            session={
                "player": {
                    "episode": episode.id,
                    "current_time": 1000,
                    "playback_rate": 1.2,
                }
            },
        )

        assert player.current_time == 1000
        assert player.playback_rate == 1.2
        current_episode = player.eject(mark_completed=True)

        assert current_episode == episode

        assert not player
        assert player.current_time == 0
        assert player.playback_rate == 1.0

        log = AudioLog.objects.get(episode=episode, user=user)
        assert log.completed
        assert log.current_time == 0

    def test_is_playing_true(self, rf, episode, user):
        player = self.make_player(
            rf,
            user=user,
            session={
                "player": {
                    "episode": episode.id,
                    "current_time": 1000,
                    "playback_rate": 1.2,
                }
            },
        )

        assert player.is_playing(episode)

    def test_is_playing_anonymous(self, rf, episode, anonymous_user):
        player = self.make_player(
            rf,
            user=anonymous_user,
            session={
                "player": {
                    "episode": episode.id,
                    "current_time": 1000,
                    "playback_rate": 1.2,
                }
            },
        )

        assert not player.is_playing(episode)

    def test_is_playing_false(self, rf, episode, user):
        player = self.make_player(
            rf,
            user=user,
            session={
                "player": {
                    "episode": 12345,
                    "current_time": 1000,
                    "playback_rate": 1.2,
                }
            },
        )

        assert not player.is_playing(episode)

    def test_is_playing_empty(self, rf, episode, user):
        player = self.make_player(rf, user=user)
        assert not player.is_playing(episode)

    def test_create_audio_log_new(self, rf, episode, user):
        player = self.make_player(rf, user=user)
        log, created = player.create_audio_log(episode, current_time=1000)
        assert created
        assert log.current_time == 1000

    def test_create_audio_log_existing(self, rf, episode, user):
        last_logged_at = timezone.now() - datetime.timedelta(days=2)
        player = self.make_player(rf, user=user)
        AudioLogFactory(
            user=user, episode=episode, current_time=1000, updated=last_logged_at
        )
        log, created = player.create_audio_log(episode, current_time=1030)
        assert not created
        assert log.current_time == 1030
        assert log.updated > last_logged_at
