from typing import Callable

import freezegun
import pytest

from django.contrib.auth.models import AnonymousUser

from audiotrails.common.typedefs import AuthenticatedUser
from audiotrails.podcasts.factories import (
    CategoryFactory,
    FollowFactory,
    PodcastFactory,
)
from audiotrails.podcasts.models import Category, Follow, Podcast
from audiotrails.users.factories import UserFactory


@pytest.fixture
def freeze_time() -> Callable:
    return freezegun.freeze_time


@pytest.fixture
def user(db) -> AuthenticatedUser:
    return UserFactory()


@pytest.fixture
def anonymous_user() -> AnonymousUser:
    return AnonymousUser


@pytest.fixture
def auth_user(client, user) -> AuthenticatedUser:
    client.force_login(user)
    return user


@pytest.fixture
def podcast(db) -> Podcast:
    return PodcastFactory()


@pytest.fixture
def category(db) -> Category:
    return CategoryFactory()


@pytest.fixture
def follow(auth_user, podcast) -> Follow:
    return FollowFactory(podcast=podcast, user=auth_user)