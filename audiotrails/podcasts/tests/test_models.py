from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.test import RequestFactory, SimpleTestCase, TestCase

from audiotrails.episodes.factories import (
    AudioLogFactory,
    EpisodeFactory,
    FavoriteFactory,
)
from audiotrails.users.factories import UserFactory

from ..factories import (
    CategoryFactory,
    FollowFactory,
    PodcastFactory,
    RecommendationFactory,
)
from ..models import Category, Podcast, Recommendation


class RecommendationManagerTests(TestCase):
    def test_bulk_delete(self) -> None:
        RecommendationFactory.create_batch(3)
        Recommendation.objects.bulk_delete()
        self.assertEqual(Recommendation.objects.count(), 0)

    def test_for_user(self) -> None:

        user = UserFactory()
        following = FollowFactory(user=user).podcast
        favorited = FavoriteFactory(user=user).episode.podcast
        listened = AudioLogFactory(user=user).episode.podcast

        received = RecommendationFactory(
            podcast=FollowFactory(user=user).podcast
        ).recommended
        user.recommended_podcasts.add(received)

        first = RecommendationFactory(podcast=following).recommended
        second = RecommendationFactory(podcast=favorited).recommended
        third = RecommendationFactory(podcast=listened).recommended

        # already received

        # not connected
        RecommendationFactory()

        # already following, listened to or favorited
        RecommendationFactory(recommended=following)
        RecommendationFactory(recommended=favorited)
        RecommendationFactory(recommended=listened)

        recommended = [r.recommended for r in Recommendation.objects.for_user(user)]

        self.assertEqual(len(recommended), 3)
        self.assertTrue(first in recommended)
        self.assertTrue(second in recommended)
        self.assertTrue(third in recommended)


class CategoryManagerTests(TestCase):
    def test_search(self):
        CategoryFactory(name="testing")
        self.assertEqual(Category.objects.search("testing").count(), 1)


class CategoryModelTests(SimpleTestCase):
    def test_slug(self):
        category = Category(name="Testing")
        self.assertEqual(category.slug, "testing")


class PodcastManagerTests(TestCase):
    def test_search(self):
        PodcastFactory(title="testing")
        self.assertEqual(Podcast.objects.search("testing").count(), 1)

    def test_with_follow_count(self):
        following_1 = PodcastFactory()
        following_2 = PodcastFactory()
        not_following = PodcastFactory()

        FollowFactory(podcast=following_1)
        FollowFactory(podcast=following_1)
        FollowFactory(podcast=following_2)

        podcasts = Podcast.objects.with_follow_count().order_by("-follow_count")

        self.assertEqual(podcasts[0].id, following_1.id)
        self.assertEqual(podcasts[1].id, following_2.id)
        self.assertEqual(podcasts[2].id, not_following.id)

        self.assertEqual(podcasts[0].follow_count, 2)
        self.assertEqual(podcasts[1].follow_count, 1)
        self.assertEqual(podcasts[2].follow_count, 0)


class PodcastModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.podcast = PodcastFactory(title="Testing")
        cls.user = UserFactory()

    def test_slug(self):
        self.assertEqual(self.podcast.slug, "testing")

    def test_get_episode_count(self):
        EpisodeFactory.create_batch(3)
        EpisodeFactory.create_batch(3, podcast=self.podcast)
        self.assertEqual(self.podcast.get_episode_count(), 3)

    def test_get_cached_episode_count(self):
        EpisodeFactory.create_batch(3)
        EpisodeFactory.create_batch(3, podcast=self.podcast)
        self.assertEqual(self.podcast.get_cached_episode_count(), 3)

    def test_slug_if_title_empty(self):
        self.assertEqual(Podcast().slug, "podcast")

    def is_following_anonymous(self):
        self.assertFalse(self.podcast.is_following(AnonymousUser()))

    def is_following_false(self):
        self.assertFalse(self.podcast.is_following(UserFactory()))

    def is_following_true(self):
        sub = FollowFactory(podcast=self.podcast)
        self.assertTrue(self.podcast.is_following(sub.user))

    def test_get_opengraph_data(self):
        req = RequestFactory().get("/")
        req.site = Site.objects.get_current()
        og_data = self.podcast.get_opengraph_data(req)
        self.assertTrue(self.podcast.title in og_data["title"])
        self.assertEqual(
            og_data["url"], "http://testserver" + self.podcast.get_absolute_url()
        )
