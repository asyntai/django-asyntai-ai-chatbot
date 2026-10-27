"""Tests for the system checks that run with `manage.py check`."""
from django.core import checks
from django.test import SimpleTestCase, override_settings

WIDGET_ID = 'asyntai_ab12cd34'
OURS = 'django_asyntai.middleware.AsyntaiWidgetMiddleware'
GZIP = 'django.middleware.gzip.GZipMiddleware'


def ids():
    return [message.id for message in checks.run_checks()
            if message.id.startswith('django_asyntai.')]


class CheckTests(SimpleTestCase):
    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_a_good_setup_is_quiet(self):
        self.assertEqual(ids(), [])

    @override_settings(ASYNTAI_WIDGET_ID='')
    def test_no_id_is_quiet(self):
        # An empty ID is how you switch the chat off, so it is not a mistake.
        self.assertEqual(ids(), [])

    @override_settings(ASYNTAI_WIDGET_ID='my widget')
    def test_a_bad_id_warns(self):
        self.assertEqual(ids(), ['django_asyntai.W001'])

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SCRIPT_URL='http://example.com/w.js')
    def test_a_bad_script_address_warns(self):
        self.assertEqual(ids(), ['django_asyntai.W002'])

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, MIDDLEWARE=[OURS, GZIP])
    def test_our_middleware_above_gzip_warns(self):
        self.assertEqual(ids(), ['django_asyntai.W003'])

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, MIDDLEWARE=[GZIP, OURS])
    def test_our_middleware_below_gzip_is_quiet(self):
        self.assertEqual(ids(), [])
