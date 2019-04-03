from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.templatetags.static import static
from django.views.decorators.cache import cache_page
from strategy_field.utils import import_by_name

import bitcaster
from bitcaster.models import Channel


@cache_page(60 * 60 * 24)
def channel_icon(request, pk):
    ch = Channel.objects.get(pk=pk)
    return plugin_icon(request, ch.handler.fqn)


def resource(path):
    return


@cache_page(60 * 60 * 24, key_prefix=bitcaster.get_full_version())
def plugin_icon(request, fqn):
    h = import_by_name(fqn)
    if h.icon and h.icon.startswith('/'):
        return HttpResponseRedirect(static(h.icon))
    elif h.icon:
        icon = Path(settings.STATIC_ROOT) / f'bitcaster/images/icons/{h.icon}.png'
    else:
        name = fqn.split('.')[-1]
        icon = Path(settings.STATIC_ROOT) / f'bitcaster/images/icons/{name.lower()}.png'
    try:
        image = icon.read_bytes()
    except (Exception, FileNotFoundError):
        return HttpResponseRedirect(static('/bitcaster/images/icons/plugin.png'))
    return HttpResponse(image, content_type='image/png')
    # return HttpResponseRedirect(static('/bitcaster/images/icons/plugin.png'))
