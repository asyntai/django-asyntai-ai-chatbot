# django-asyntai-ai-chatbot

Adds the [Asyntai](https://asyntai.com) AI chat assistant to a Django site.
The assistant answers visitor questions from your own content, day and night,
in more than 80 languages.

Free and open source. Works on every Asyntai plan, including the free plan.

- Requires Django 4.2 or newer and Python 3.10 or newer
- Documentation: https://asyntai.com/documentation/integrations/django/

## Install

```
pip install django-asyntai-ai-chatbot
```

Add the app to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_asyntai",
]
```

Add the middleware at the end of `MIDDLEWARE`:

```python
MIDDLEWARE = [
    # ...
    "django_asyntai.middleware.AsyntaiWidgetMiddleware",
]
```

Put your widget ID in your settings file:

```python
ASYNTAI_WIDGET_ID = "asyntai_ab12cd34"
```

You get the ID from the Install page of your
[Asyntai dashboard](https://asyntai.com/dashboard). You can paste the whole
snippet; the package keeps only the ID.

That is all. The chat button appears on every page of the site. No template
edit and no migration.

## Settings

```python
ASYNTAI_WIDGET_ID = "asyntai_ab12cd34"          # required; empty switches the chat off
ASYNTAI_SHOW_TO_ANONYMOUS_ONLY = False           # optional; hide the chat from signed-in users
ASYNTAI_SKIP_PREFIXES = ["/admin/"]              # optional; paths the widget never touches
ASYNTAI_SCRIPT_URL = "https://widget.asyntai.com/static/js/chat-widget.js"  # optional
```

The values are read on every request, so you can keep the ID in an
environment variable:

```python
import os
ASYNTAI_WIDGET_ID = os.environ.get("ASYNTAI_WIDGET_ID", "")
```

Set `ASYNTAI_SKIP_PREFIXES` when your admin lives somewhere other than
`/admin/`. Change `ASYNTAI_SCRIPT_URL` only if Asyntai support asks you to.

## Placing the widget by hand

Leave the middleware out and put the tag where you want it instead:

```html
{% load asyntai %}
...
{% asyntai_widget %}
</body>
```

The tag needs the request in the template context, which Django's default
`django.template.context_processors.request` provides. The tag and the
middleware never both fire, so it is safe to keep both.

## GZipMiddleware

If you use `GZipMiddleware`, list `AsyntaiWidgetMiddleware` below it, so the
widget goes into the page before the page is compressed. `manage.py check`
warns you when the order is wrong.

## How it works

The middleware inserts a small script just before the closing body tag of
every HTML page. That script waits for the page to finish loading, then
fetches the chat widget from Asyntai, so your site draws first and page speed
is unchanged.

The widget ID and the script address travel to the browser on a data
attribute, never inside the script. Only an `https` script address is
accepted.

The middleware leaves alone: the admin, anything that is not `text/html`, any
status other than 200, a streaming response, a body another middleware has
compressed, a page with no closing body tag, and a page that already carries
the widget.

## Checks

`manage.py check` reports three mistakes:

| ID | Meaning |
| --- | --- |
| `django_asyntai.W001` | `ASYNTAI_WIDGET_ID` is not a valid widget ID. |
| `django_asyntai.W002` | `ASYNTAI_SCRIPT_URL` is not an `https` address. |
| `django_asyntai.W003` | The middleware is listed above `GZipMiddleware`. |

## Tests

```
pip install django
PYTHONPATH=src:. python -m django test --settings=tests.settings
```

## Support

hello@asyntai.com

## Licence

MIT. See [LICENSE](LICENSE).
