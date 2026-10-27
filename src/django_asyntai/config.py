"""Working out what the chat widget should do on this request.

Everything comes from the project's settings file:

    ASYNTAI_WIDGET_ID                 the ID from the Asyntai dashboard
    ASYNTAI_SHOW_TO_ANONYMOUS_ONLY    hide the chat from signed-in users
    ASYNTAI_SCRIPT_URL                change only if Asyntai support asks

The values are read on every request, so a project can keep the ID in an
environment variable and change it without a code change.
"""
from django.conf import settings

from .utils import DEFAULT_SCRIPT_URL, clean_script_url, clean_widget_id


def get_widget_context(request):
    """Return what the template needs, or None when the chat must stay off."""
    widget_id = clean_widget_id(getattr(settings, 'ASYNTAI_WIDGET_ID', ''))
    if not widget_id:
        return None

    script_url = clean_script_url(getattr(settings, 'ASYNTAI_SCRIPT_URL', DEFAULT_SCRIPT_URL))
    if not script_url:
        return None

    anonymous_only = bool(getattr(settings, 'ASYNTAI_SHOW_TO_ANONYMOUS_ONLY', False))
    if anonymous_only and _is_signed_in(request):
        return None

    return {'asyntai_widget_id': widget_id, 'asyntai_script_url': script_url}


def _is_signed_in(request):
    user = getattr(request, 'user', None)
    return bool(user is not None and getattr(user, 'is_authenticated', False))
