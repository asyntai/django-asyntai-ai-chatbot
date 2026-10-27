"""System checks, shown by `manage.py check` and on every runserver start.

They catch the two mistakes that leave the chat silently missing: a widget ID
that does not have the right shape, and a middleware order in which the page
is already compressed before this package sees it.
"""
from django.conf import settings
from django.core.checks import Warning, register

from .utils import clean_script_url, clean_widget_id

MIDDLEWARE_PATH = 'django_asyntai.middleware.AsyntaiWidgetMiddleware'
GZIP_PATH = 'django.middleware.gzip.GZipMiddleware'


@register()
def check_settings(app_configs, **kwargs):
    messages = []

    raw_id = getattr(settings, 'ASYNTAI_WIDGET_ID', '')
    if raw_id and not clean_widget_id(raw_id):
        messages.append(Warning(
            'ASYNTAI_WIDGET_ID is set, but it is not a valid widget ID, so the chat stays off.',
            hint='Copy the ID from your Asyntai dashboard. It looks like asyntai_ab12cd34.',
            id='django_asyntai.W001',
        ))

    raw_url = getattr(settings, 'ASYNTAI_SCRIPT_URL', None)
    if raw_url is not None and not clean_script_url(raw_url):
        messages.append(Warning(
            'ASYNTAI_SCRIPT_URL must be an https address, so the chat stays off.',
            hint='Remove the setting to use the Asyntai address.',
            id='django_asyntai.W002',
        ))

    middleware = list(getattr(settings, 'MIDDLEWARE', None) or [])
    if MIDDLEWARE_PATH in middleware and GZIP_PATH in middleware:
        if middleware.index(MIDDLEWARE_PATH) < middleware.index(GZIP_PATH):
            messages.append(Warning(
                'AsyntaiWidgetMiddleware is listed above GZipMiddleware, so it gets '
                'pages that are already compressed and cannot add the chat.',
                hint='Move AsyntaiWidgetMiddleware below GZipMiddleware in MIDDLEWARE.',
                id='django_asyntai.W003',
            ))

    return messages
