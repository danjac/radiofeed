import pathlib
import socket

from email.utils import getaddresses

import environ

from django.contrib import messages
from django.urls import reverse_lazy

env = environ.Env()

DEBUG = False

BASE_DIR = pathlib.Path(__file__).absolute().parents[3]

SECRET_KEY = env("SECRET_KEY")

DATABASES = {
    "default": env.db(),
}

# prevent deprecation warnings
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REDIS_URL = env("REDIS_URL")

CACHES = {"default": env.cache("REDIS_URL")}

DEFAULT_CACHE_TIMEOUT = 3600

EMAIL_HOST = env("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"

ATOMIC_REQUESTS = True

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# configure internal IPS inside docker container

INTERNAL_IPS = [
    ip[:-1] + "1" for ip in socket.gethostbyname_ex(socket.gethostname())[2]
]

ADMINS = getaddresses(env.list("ADMINS", default=[]))

SITE_ID = 1

SESSION_COOKIE_DOMAIN = env("SESSION_COOKIE_DOMAIN", default=None)
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN", default=None)
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

ROOT_URLCONF = "jcasts.config.urls"

ASGI_APPLICATION = "jcasts.config.asgi.application"

LOCAL_APPS = [
    "jcasts.episodes",
    "jcasts.podcasts",
    "jcasts.users",
]


INSTALLED_APPS = [
    "django.forms",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "django_extensions",
    "django_celery_beat",
    "django_htmx",
    "djcelery_email",
    "widget_tweaks",
] + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django_permissions_policy.PermissionsPolicyMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "jcasts.shared.middleware.CacheControlMiddleware",
    "jcasts.shared.middleware.SearchMiddleware",
    "jcasts.episodes.middleware.PlayerMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "jcasts.shared.middleware.HtmxMessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

DEFAULT_PAGE_SIZE = 30

# base Django admin URL (should be something obscure in production)

ADMIN_URL = env("ADMIN_URL", default="admin/")

# auth

AUTH_USER_MODEL = "users.User"

# https://docs.djangoproject.com/en/dev/ref/settings/#authentication-backends

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

HOME_URL = reverse_lazy("episodes:index")
LOGIN_REDIRECT_URL = reverse_lazy("episodes:index")

LOGIN_URL = "account_login"

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_LOGIN_ON_PASSWORD_RESET = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = "en"
LANGUAGES = [
    ("en", "English (US)"),
    ("en-gb", "English (GB)"),
]
LANGUAGE_COOKIE_DOMAIN = env("LANGUAGE_COOKIE_DOMAIN", default=None)
LANGUAGE_COOKIE_SAMESITE = "Lax"

LOCALE_PATHS = [BASE_DIR / "i18n"]

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# https://docs.djangoproject.com/en/1.11/ref/forms/renderers/

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# https://docs.djangoproject.com/en/3.0/ref/contrib/messages/

MESSAGE_TAGS = {
    messages.DEBUG: "message-debug",
    messages.INFO: "message-info",
    messages.SUCCESS: "message-success",
    messages.WARNING: "message-warning",
    messages.ERROR: "message-error",
}

# https://celery.readthedocs.io/en/latest/userguide/configuration.html

result_backend = CELERY_BROKER_URL = REDIS_URL
result_serializer = "json"
task_acks_late = True
task_track_started = True

# https://django-taggit.readthedocs.io/en/latest/getting_started.html

STATIC_URL = env("STATIC_URL", default="/static/")
STATICFILES_DIRS = [BASE_DIR / "assets"]

TEMPLATES: list[dict] = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "debug": DEBUG,
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "jcasts.shared.template.context_processors.is_cookies_accepted",
                "jcasts.shared.template.context_processors.search",
            ],
            "builtins": [
                "jcasts.shared.template.defaulttags",
            ],
            "libraries": {
                "pagination": "jcasts.shared.pagination.templatetags",
            },
        },
    }
]


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "null": {"level": "DEBUG", "class": "logging.NullHandler"},
    },
    "loggers": {
        "root": {"handlers": ["console"], "level": "INFO"},
        "django.security.DisallowedHost": {"handlers": ["null"], "propagate": False},
        "django.request": {"handlers": ["console"], "level": "ERROR"},
    },
}

PRIVACY_DETAILS = {
    "contact_email": env("CONTACT_EMAIL", default="admin@localhost"),
    "host_country": env("HOST_COUNTRY", default="Finland"),
    "age_of_consent": env.int("AGE_OF_CONSENT", default=18),
}

GRAVATAR_DEFAULT_SIZE = 30
GRAVATAR_DEFAULT_IMAGE = env("GRAVATAR_DEFAULT_IMAGE", default="retro")
GRAVATAR_DEFAULT_RATING = env("GRAVATAR_DEFAULT_RATING", default="g")

DEFAULT_ITUNES_LIMIT = env.int("DEFAULT_ITUNES_LIMIT", default=DEFAULT_PAGE_SIZE)

TWITTER_ACCOUNT = env("TWITTER_ACCOUNT", default=None)
