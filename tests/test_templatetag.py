"""Tests for placing the widget by hand with {% asyntai_widget %}."""
from django.template import Context, Template
from django.test import Client, TestCase, override_settings

WIDGET_ID = 'asyntai_ab12cd34'
MARKER = 'asyntai-widget-config'


class TemplateTagTests(TestCase):
    def setUp(self):
        self.client = Client()

    @override_settings(ASYNTAI_WIDGET_ID='')
    def test_the_tag_renders_nothing_when_the_chat_is_off(self):
        self.assertNotIn(MARKER, self.client.get('/tag/').content.decode())

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_the_tag_renders_the_widget(self):
        html = self.client.get('/tag/').content.decode()
        self.assertIn('data-asyntai-widget="%s"' % WIDGET_ID, html)

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_the_markup_is_not_escaped(self):
        html = self.client.get('/tag/').content.decode()
        self.assertNotIn('&lt;script&gt;', html)
        self.assertIn('<script>', html)

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_the_middleware_does_not_add_a_second_copy(self):
        html = self.client.get('/tag/').content.decode()
        self.assertEqual(html.count('data-asyntai-widget='), 1)

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_the_tag_sits_where_the_template_puts_it(self):
        html = self.client.get('/tag/').content.decode()
        self.assertLess(html.index('Placed by hand'), html.index(MARKER))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_a_template_without_the_request_renders_nothing(self):
        rendered = Template('{% load asyntai %}{% asyntai_widget %}').render(Context({}))
        self.assertEqual(rendered, '')
