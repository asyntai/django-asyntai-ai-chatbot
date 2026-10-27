"""Tests for putting the widget on a page."""
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

WIDGET_ID = 'asyntai_ab12cd34'
MARKER = 'asyntai-widget-config'


@override_settings(ASYNTAI_WIDGET_ID=WIDGET_ID)
class MiddlewareTests(TestCase):
    def setUp(self):
        self.client = Client()

    def body(self, url='/'):
        return self.client.get(url).content.decode()

    @override_settings(ASYNTAI_WIDGET_ID='')
    def test_nothing_is_added_when_the_chat_is_off(self):
        self.assertNotIn(MARKER, self.body())

    def test_the_widget_lands_on_a_page(self):
        html = self.body()
        self.assertIn(MARKER, html)
        self.assertIn('data-asyntai-widget="%s"' % WIDGET_ID, html)

    def test_the_widget_sits_before_the_closing_body_tag(self):
        html = self.body()
        self.assertLess(html.index(MARKER), html.rindex('</body>'))

    def test_only_one_copy(self):
        self.assertEqual(self.body().count('data-asyntai-widget='), 1)

    def test_the_last_closing_body_tag_is_used(self):
        html = self.body('/two-body-tags/')
        self.assertLess(html.index('&lt;/body&gt;'), html.index(MARKER))

    def test_a_page_without_a_closing_body_tag_is_left_alone(self):
        self.assertNotIn(MARKER, self.body('/fragment/'))

    def test_json_is_left_alone(self):
        self.assertNotIn(MARKER, self.body('/json/'))

    def test_a_missing_page_is_left_alone(self):
        self.assertNotIn(MARKER, self.body('/missing/'))

    def test_a_streaming_response_is_left_alone(self):
        response = self.client.get('/streaming/')
        self.assertNotIn(MARKER, b''.join(response.streaming_content).decode())

    def test_a_page_that_already_has_the_widget_is_left_alone(self):
        self.assertEqual(self.body('/already/').count('data-asyntai-id'), 1)

    def test_the_django_admin_is_left_alone(self):
        self.assertNotIn(MARKER, self.body('/admin/login/'))

    @override_settings(ASYNTAI_SKIP_PREFIXES=['/two-body-tags/'])
    def test_a_project_can_name_its_own_paths_to_skip(self):
        self.assertNotIn(MARKER, self.body('/two-body-tags/'))
        self.assertIn(MARKER, self.body())

    @override_settings(ASYNTAI_SKIP_PREFIXES=[])
    def test_an_empty_skip_list_skips_nothing(self):
        self.assertIn(MARKER, self.body('/admin/login/'))

    def test_content_length_matches_the_new_body(self):
        response = self.client.get('/content-length/')
        self.assertIn(MARKER, response.content.decode())
        self.assertEqual(int(response['Content-Length']), len(response.content))

    def test_a_compressed_body_is_left_alone(self):
        response = self.client.get('/compressed/')
        self.assertNotIn(b'asyntai-widget-config', response.content)

    @override_settings(ASYNTAI_WIDGET_ID='asyntai_ab12cd34" onload="alert(1)')
    def test_the_id_cannot_break_out_of_the_attribute(self):
        self.assertNotIn('onload=', self.body())

    @override_settings(ASYNTAI_SHOW_TO_ANONYMOUS_ONLY=True)
    def test_signed_out_only_hides_the_chat_from_a_member(self):
        User.objects.create_user('member', password='secret-for-tests')
        self.client.login(username='member', password='secret-for-tests')
        self.assertNotIn(MARKER, self.body())

    @override_settings(ASYNTAI_SHOW_TO_ANONYMOUS_ONLY=True)
    def test_signed_out_only_shows_the_chat_to_a_visitor(self):
        self.assertIn(MARKER, self.body())


@override_settings(
    ASYNTAI_WIDGET_ID=WIDGET_ID,
    MIDDLEWARE=[
        'django.middleware.gzip.GZipMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django_asyntai.middleware.AsyntaiWidgetMiddleware',
    ],
)
class GzipOrderTests(TestCase):
    def test_the_widget_is_added_before_gzip_compresses_the_page(self):
        response = Client(HTTP_ACCEPT_ENCODING='gzip').get('/long/')
        self.assertEqual(response['Content-Encoding'], 'gzip')
        import gzip
        self.assertIn(b'asyntai-widget-config', gzip.decompress(response.content))
