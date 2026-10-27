"""Tests for working out what the widget should do on a request."""
from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, override_settings
from django_asyntai.config import get_widget_context
from django_asyntai.utils import DEFAULT_SCRIPT_URL

WIDGET_ID = 'asyntai_ab12cd34'


class GetWidgetContextTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def request(self, signed_in=False):
        request = self.factory.get('/')
        if signed_in:
            request.user = User.objects.create_user('member', password='x')
        else:
            request.user = AnonymousUser()
        return request

    def test_no_setting_means_no_widget(self):
        self.assertIsNone(get_widget_context(self.request()))

    @override_settings(ASYNTAI_WIDGET_ID='')
    def test_an_empty_setting_means_no_widget(self):
        self.assertIsNone(get_widget_context(self.request()))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_the_setting_is_used(self):
        context = get_widget_context(self.request())
        self.assertEqual(context['asyntai_widget_id'], WIDGET_ID)
        self.assertEqual(context['asyntai_script_url'], DEFAULT_SCRIPT_URL)

    @override_settings(ASYNTAI_WIDGET_ID='<script data-asyntai-id="%s"></script>' % WIDGET_ID)
    def test_a_pasted_snippet_is_accepted(self):
        self.assertEqual(get_widget_context(self.request())['asyntai_widget_id'], WIDGET_ID)

    @override_settings(ASYNTAI_WIDGET_ID='not-an-id')
    def test_a_bad_id_means_no_widget(self):
        self.assertIsNone(get_widget_context(self.request()))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SCRIPT_URL='javascript:alert(1)')
    def test_a_bad_script_address_means_no_widget(self):
        self.assertIsNone(get_widget_context(self.request()))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SCRIPT_URL='https://cdn.example.com/w.js')
    def test_a_custom_https_script_address_is_used(self):
        self.assertEqual(get_widget_context(self.request())['asyntai_script_url'],
                         'https://cdn.example.com/w.js')

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SHOW_TO_ANONYMOUS_ONLY=True)
    def test_signed_out_only_hides_the_chat_from_a_member(self):
        self.assertIsNone(get_widget_context(self.request(signed_in=True)))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SHOW_TO_ANONYMOUS_ONLY=True)
    def test_signed_out_only_still_shows_the_chat_to_a_visitor(self):
        self.assertIsNotNone(get_widget_context(self.request()))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
    def test_a_member_sees_the_chat_when_the_switch_is_off(self):
        self.assertIsNotNone(get_widget_context(self.request(signed_in=True)))

    @override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID, ASYNTAI_SHOW_TO_ANONYMOUS_ONLY=True)
    def test_a_request_with_no_user_is_treated_as_a_visitor(self):
        self.assertIsNotNone(get_widget_context(self.factory.get('/')))
