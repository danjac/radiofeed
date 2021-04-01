from django.core.management.base import BaseCommand

from audiotrails.podcasts.recommender import recommend


class Command(BaseCommand):
    help = "Creates new podcast recommendations."

    def handle(self, *args, **kwargs):
        recommend()