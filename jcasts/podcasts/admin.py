from __future__ import annotations

from typing import Iterable

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest

from jcasts.podcasts.models import Category, Podcast
from jcasts.podcasts.tasks import sync_podcast_feed


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ordering = ("name",)
    list_display = ("name", "parent", "itunes_genre_id")
    search_fields = ("name",)


class PubDateFilter(admin.SimpleListFilter):
    title = "Pub date"
    parameter_name = "pub_date"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> Iterable[tuple[str, str]]:
        return (
            ("yes", "With pub date"),
            ("no", "With no pub date"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value == "yes":
            return queryset.filter(pub_date__isnull=False)
        if value == "no":
            return queryset.filter(pub_date__isnull=True)
        return queryset


class PromotedFilter(admin.SimpleListFilter):
    title = "Promoted"
    parameter_name = "promoted"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> Iterable[tuple[str, str]]:
        return (("yes", "Promoted"),)

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value == "yes":
            return queryset.filter(promoted=True)
        return queryset


class ActiveFilter(admin.SimpleListFilter):
    title = "Active"
    parameter_name = "active"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> Iterable[tuple[str, str]]:
        return (
            ("yes", "Active"),
            ("no", "Inactive"),
        )

    def queryset(self, request: HttpRequest, queryset: QuerySet) -> QuerySet:
        value = self.value()
        if value == "yes":
            return queryset.filter(active=True)
        if value == "no":
            return queryset.filter(active=False)
        return queryset


@admin.register(Podcast)
class PodcastAdmin(admin.ModelAdmin):
    list_filter = (PubDateFilter, ActiveFilter, PromotedFilter)

    ordering = ("-pub_date",)
    list_display = (
        "__str__",
        "source",
        "pub_date",
        "active",
        "promoted",
        "num_episodes",
    )
    list_editable = ("promoted",)
    search_fields = ("search_document",)

    raw_id_fields = (
        "recipients",
        "redirect_to",
    )

    readonly_fields = ("created", "updated", "pub_date", "num_episodes")

    actions = ["reactivate", "sync_podcast_feeds"]

    @admin.action(description="Re-activate podcasts")
    def reactivate(self, request: HttpRequest, queryset: QuerySet):
        num_updated = queryset.filter(active=False).update(
            active=True, error_status=None
        )
        self.message_user(
            request,
            f"{num_updated} podcasts re-activated",
            messages.SUCCESS,
        )

    @admin.action(description="Sync podcast feeds")
    def sync_podcast_feeds(self, request: HttpRequest, queryset: QuerySet):

        for rss in queryset.values_list("rss", flat=True):
            sync_podcast_feed.delay(rss, force_update=True)

        self.message_user(
            request,
            f"{queryset.count()} podcast(s) scheduled for update",
            messages.SUCCESS,
        )

    def source(self, obj: Podcast) -> str:
        return obj.get_domain()

    def get_search_results(
        self, request: HttpRequest, queryset: QuerySet, search_term: str
    ) -> QuerySet:
        if not search_term:
            return super().get_search_results(request, queryset, search_term)
        return queryset.search(search_term).order_by("-rank", "-pub_date"), False
