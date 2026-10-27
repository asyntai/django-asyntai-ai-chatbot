"""Views the middleware tests run against."""
import gzip

from django.http import (HttpResponse, HttpResponseNotFound,
                         JsonResponse, StreamingHttpResponse)
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib import admin

PAGE = '<html><head><title>Test</title></head><body><h1>Hello</h1></body></html>'


def html_page(request):
    return HttpResponse(PAGE)


def html_without_body(request):
    return HttpResponse('<p>A fragment with no closing body tag.</p>',
                        content_type='text/html')


def two_body_tags(request):
    # A page that prints the closing tag inside a code sample. Only the real
    # one at the end may be used.
    return HttpResponse('<html><body><code>&lt;/body&gt;</code>'
                        '</body></html>')


def json_page(request):
    return JsonResponse({'hello': 'world'})


def missing_page(request):
    return HttpResponseNotFound(PAGE)


def streaming_page(request):
    return StreamingHttpResponse(iter([PAGE]), content_type='text/html')


def already_has_widget(request):
    return HttpResponse('<html><body>'
                        '<script src="https://widget.asyntai.com/static/js/chat-widget.js" '
                        'data-asyntai-id="asyntai_ab12cd34"></script>'
                        '</body></html>')


def with_content_length(request):
    response = HttpResponse(PAGE)
    response['Content-Length'] = str(len(response.content))
    return response


def compressed_page(request):
    # A body another middleware has already gzipped is no longer html we can
    # read, so ours must not touch it.
    response = HttpResponse(gzip.compress(PAGE.encode()), content_type='text/html')
    response['Content-Encoding'] = 'gzip'
    return response


def long_page(request):
    # GZipMiddleware skips bodies under 200 bytes, so this one is longer.
    return HttpResponse('<html><body>' + '<p>Long text.</p>' * 40 + '</body></html>')


def tag_page(request):
    return TemplateResponse(request, 'tag_page.html', {})


urlpatterns = [
    path('', html_page),
    path('fragment/', html_without_body),
    path('two-body-tags/', two_body_tags),
    path('json/', json_page),
    path('missing/', missing_page),
    path('streaming/', streaming_page),
    path('already/', already_has_widget),
    path('content-length/', with_content_length),
    path('compressed/', compressed_page),
    path('long/', long_page),
    path('tag/', tag_page),
    path('admin/', admin.site.urls),
]
