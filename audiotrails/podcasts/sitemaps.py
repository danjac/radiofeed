import datetime

from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from .models import Category, Podcast


class CategorySitemap(Sitemap):
    changefreq = "never"
    priority = 0.3

    def items(self):
        return Category.objects.order_by("name")


class PodcastSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.5
    limit = 100

    def items(self):
        return Podcast.objects.filter(
            pub_date__isnull=False,
            pub_date__gt=timezone.now() - datetime.timedelta(hours=24),
        ).order_by("-pub_date")

    def lastmod(self, item):
        return item.pub_date