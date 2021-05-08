from .base import *  # noqa
from .mixins.aws import *  # noqa
from .mixins.aws import AWS_CLOUDFRONT_STATIC_DOMAIN, AWS_STATIC_LOCATION
from .mixins.mailgun import *  # noqa
from .mixins.secure import *  # noqa
from .mixins.sentry import *  # noqa

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# https://pypi.org/project/django-permissions-policy/

PERMISSIONS_POLICY = {
    "accelerometer": [],
    "ambient-light-sensor": [],
    "camera": [],
    "document-domain": [],
    "encrypted-media": [],
    "fullscreen": [],
    "geolocation": [],
    "gyroscope": [],
    "interest-cohort": [],
    "magnetometer": [],
    "microphone": [],
    "payment": [],
    "usb": [],
}

STATIC_URL = AWS_CLOUDFRONT_STATIC_DOMAIN + "/" + AWS_STATIC_LOCATION
