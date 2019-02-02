# -*- coding: utf-8 -*-
from django.shortcuts import render


def handler404(request, *args, **kwargs):
    response = render(request, 'bitcaster/404.html')
    response.status_code = 404
    return response


def handler500(request, *args, **kwargs):
    response = render(request, 'bitcaster/500.html', {})
    response.status_code = 500
    return response
