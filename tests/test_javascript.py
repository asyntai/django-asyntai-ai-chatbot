"""The script the widget puts on the page must parse in a browser.

A template only becomes real text when it renders, so this checks the
rendered page, not the template file.
"""
import os
import shutil
import subprocess
import tempfile

from django.test import Client, TestCase, override_settings


@override_settings(ASYNTAI_WIDGET_ID='asyntai_ab12cd34')
class JavaScriptTests(TestCase):
    def script_from(self, url):
        html = Client().get(url).content.decode()
        start = html.index('<script>', html.index('asyntai-widget-config'))
        end = html.index('</script>', start)
        return html[start + len('<script>'):end]

    def check(self, source):
        node = shutil.which('node')
        if not node:
            self.skipTest('node is not installed')

        handle, path = tempfile.mkstemp(suffix='.js')
        with os.fdopen(handle, 'w', encoding='utf-8') as fh:
            fh.write(source)
        try:
            result = subprocess.run([node, '--check', path], capture_output=True, text=True)
        finally:
            os.unlink(path)

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_the_script_parses_when_the_middleware_places_it(self):
        self.check(self.script_from('/'))

    def test_the_script_parses_when_the_tag_places_it(self):
        self.check(self.script_from('/tag/'))
