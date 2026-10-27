"""Tests for reading a stored value."""
from django.test import SimpleTestCase
from django_asyntai.utils import (DEFAULT_SCRIPT_URL, clean_script_url,
                                   clean_widget_id)

WIDGET_ID = 'asyntai_ab12cd34'
SNIPPET = ('<script src="https://widget.asyntai.com/static/js/chat-widget.js" '
           'data-asyntai-id="%s" async></script>' % WIDGET_ID)


class CleanWidgetIdTests(SimpleTestCase):
    def test_plain_id(self):
        self.assertEqual(clean_widget_id(WIDGET_ID), WIDGET_ID)

    def test_id_is_trimmed(self):
        self.assertEqual(clean_widget_id('  %s\n' % WIDGET_ID), WIDGET_ID)

    def test_whole_snippet(self):
        self.assertEqual(clean_widget_id(SNIPPET), WIDGET_ID)

    def test_snippet_with_single_quotes(self):
        self.assertEqual(
            clean_widget_id("<script data-asyntai-id='%s'></script>" % WIDGET_ID),
            WIDGET_ID)

    def test_snippet_with_spaces_around_equals(self):
        self.assertEqual(
            clean_widget_id('<script data-asyntai-id = "%s"></script>' % WIDGET_ID),
            WIDGET_ID)

    def test_longest_accepted_id(self):
        longest = 'asyntai_' + 'a' * 64
        self.assertEqual(clean_widget_id(longest), longest)

    def test_one_character_too_long(self):
        self.assertEqual(clean_widget_id('asyntai_' + 'a' * 65), '')

    def test_values_that_switch_the_chat_off(self):
        for raw in ['', '   ', None, 123, ['a'], 'widget_ab12cd34',
                    'asyntai_ab12', 'asyntai_ab12<script>',
                    '<script data-asyntai-id="oops"></script>',
                    'asyntai_ab12cd34" onload="alert(1)']:
            with self.subTest(raw=raw):
                self.assertEqual(clean_widget_id(raw), '')


class CleanScriptUrlTests(SimpleTestCase):
    def test_empty_falls_back_to_asyntai(self):
        self.assertEqual(clean_script_url(''), DEFAULT_SCRIPT_URL)

    def test_https_address_is_kept(self):
        self.assertEqual(clean_script_url('https://cdn.example.com/w.js'),
                         'https://cdn.example.com/w.js')

    def test_address_is_trimmed(self):
        self.assertEqual(clean_script_url('  %s  ' % DEFAULT_SCRIPT_URL),
                         DEFAULT_SCRIPT_URL)

    def test_addresses_that_are_refused(self):
        for raw in ['http://widget.asyntai.com/w.js', 'javascript:alert(1)',
                    'data:text/javascript,alert(1)', '//cdn.example.com/w.js',
                    'https://a.com/w.js" onload="alert(1)',
                    'https://a.com/w.js<script>', 'https://a.com/w js', None, 7]:
            with self.subTest(raw=raw):
                self.assertEqual(clean_script_url(raw), '')
