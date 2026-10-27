from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoAsyntaiConfig(AppConfig):
    name = 'django_asyntai'
    label = 'django_asyntai'
    verbose_name = _('Asyntai AI chat assistant')

    def ready(self):
        # Registers the system checks that warn about a bad widget ID and a
        # middleware order that would hide the widget.
        from . import checks  # noqa: F401
