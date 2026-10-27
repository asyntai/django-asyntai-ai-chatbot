"""Puts the chat widget on every page of the site, with no template edit.

The page templates belong to the project, so a middleware is the only way to
add the widget without asking the developer to change one. Anyone who prefers
to place it by hand can leave the middleware out and use the
{% asyntai_widget %} tag instead.
"""
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_str

from .config import get_widget_context

BODY_CLOSE = '</body>'

#: Paths the widget never touches by default. The Django admin is a tool for
#: staff, and a chat bubble on top of it would only be in the way.
SKIP_PREFIXES = ('/admin/',)


class AsyntaiWidgetMiddleware:
    """Inserts the widget just before the closing body tag."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not self.should_insert(request, response):
            return response

        context = get_widget_context(request)
        if context is None:
            return response

        charset = response.charset or 'utf-8'

        try:
            html = response.content.decode(charset)
        except (UnicodeDecodeError, LookupError):
            return response

        if BODY_CLOSE not in html:
            return response

        snippet = render_to_string('django_asyntai/widget.html', context, request=request)

        # Split on the last closing tag, so a page that prints the tag inside
        # an example or a code block is left alone.
        head, _, tail = html.rpartition(BODY_CLOSE)
        response.content = (head + snippet + BODY_CLOSE + tail).encode(charset)

        if response.has_header('Content-Length'):
            response['Content-Length'] = str(len(response.content))

        return response

    def skip_prefixes(self):
        """Paths to leave alone. A project can name its own admin path here."""
        prefixes = getattr(settings, 'ASYNTAI_SKIP_PREFIXES', None)
        if prefixes is None:
            return SKIP_PREFIXES
        return tuple(prefixes)

    def should_insert(self, request, response):
        """Answer whether this response can carry the widget."""
        if getattr(response, 'streaming', False):
            return False

        if response.status_code != 200:
            return False

        # A compressed body is no longer html we can read.
        if response.has_header('Content-Encoding'):
            return False

        content_type = force_str(response.get('Content-Type', ''))
        if content_type.split(';')[0].strip().lower() != 'text/html':
            return False

        path = request.path or '/'
        prefixes = self.skip_prefixes()
        if prefixes and path.startswith(prefixes):
            return False

        # Never add a second copy. Two things count as one already being
        # there: the marker this package writes, which is what the
        # {% asyntai_widget %} tag leaves behind, and a snippet the developer
        # pasted into the template by hand.
        for marker in (b'asyntai-widget-config', b'data-asyntai-id'):
            if marker in response.content:
                return False

        return True
