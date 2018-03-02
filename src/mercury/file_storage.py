# -*- coding: utf-8 -*-
"""
mercury / file_storage
~~~~~~~~~~~~~~~~~

:copyright: (c) 2018 Stefano Apostolico, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import logging

import os
from functools import wraps

from django.core.files.storage import FileSystemStorage

logger = logging.getLogger(__name__)




def _get_media_root(prefix):
    @wraps(_get_media_root)
    def media_file_name(instance, filename):
        h = instance.email
        basename, ext = os.path.splitext(filename)
        return os.path.join('mediafiles', prefix, h[0:1], h[1:2], h + ext.lower())

    return media_file_name


profile_media_root = _get_media_root('profile')
org_media_root = _get_media_root('org')
app_media_root = _get_media_root('app')


class MediaFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        if max_length and len(name) > max_length:
            raise (Exception("name's length is greater than max_length"))
        return name

    def _save(self, name, content):
        if self.exists(name):
            # if the file exists, do not call the superclasses _save method
            return name
        # if the file is new, DO call it
        return super(MediaFileSystemStorage, self)._save(name, content)
