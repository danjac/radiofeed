from django import template

from jcasts.shared.typedefs import ContextDict

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_url(context: ContextDict, page_number: int, param: str = "page") -> str:
    """
    Inserts the "page" query string parameter with the
    provided page number into the template, preserving the original
    request path and any other query string parameters.

    Given the above and a URL of "/search?q=test" the result would
    be something like:

    "/search?q=test&page=3"
    """
    request = context["request"]
    params = request.GET.copy()
    params[param] = page_number
    return request.path + "?" + params.urlencode()
