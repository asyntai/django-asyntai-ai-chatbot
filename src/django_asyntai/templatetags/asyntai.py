"""The {% asyntai_widget %} tag, for placing the widget by hand.

Use this when you would rather not run the middleware, or when the widget
must sit somewhere other than the end of the body. Load it with
{% load asyntai %} and put the tag just before </body>. The template needs
the request in its context, which the default
django.template.context_processors.request gives it.
"""
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from ..config import get_widget_context

register = template.Library()


@register.simple_tag(takes_context=True)
def asyntai_widget(context):
    """Render the widget, or nothing at all when the chat is off."""
    request = context.get('request')
    if request is None:
        return ''

    widget_context = get_widget_context(request)
    if widget_context is None:
        return ''

    # simple_tag escapes what it returns, and this is markup, not text.
    return mark_safe(
        render_to_string('django_asyntai/widget.html', widget_context, request=request)
    )
