import collections
import urllib
from typing import Any, Dict, Optional, Union

from django import template
from django.shortcuts import resolve_url
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from .html import clean_html_content
from .html import stripentities as _stripentities

register = template.Library()

ActiveLink = collections.namedtuple("Link", "url match exact")


@register.simple_tag(takes_context=True)
def active_link(context: Dict[str, Any], url_name: str, *args, **kwargs) -> ActiveLink:
    url = resolve_url(url_name, *args, **kwargs)
    if context["request"].path == url:
        return ActiveLink(url, True, True)
    elif context["request"].path.startswith(url):
        return ActiveLink(url, True, False)
    return ActiveLink(url, False, False)


@register.inclusion_tag("_share.html", takes_context=True)
def share_buttons(context: Dict[str, Any], url: str, subject: str):
    url = urllib.parse.quote(context["request"].build_absolute_uri(url))
    subject = urllib.parse.quote(subject)

    return {
        "share_urls": {
            "email": f"mailto:?subject={subject}&body={url}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={url}",
            "twitter": f"https://twitter.com/share?url={url}&text={subject}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={url}",
        }
    }


@register.filter
@stringfilter
def clean_html(value: str) -> str:
    return mark_safe(_stripentities(clean_html_content(value or "")))


@register.filter
@stringfilter
def stripentities(value: str) -> str:
    return _stripentities(value or "")


@register.filter
def percent(
    value: Optional[Union[int, float]], total: Optional[Union[int, float]]
) -> float:
    if not value or not total:
        return 0

    return (value / total) * 100
