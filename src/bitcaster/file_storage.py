import logging
import os
from functools import wraps

from django.core.files.storage import FileSystemStorage

logger = logging.getLogger(__name__)


def _get_media_root(prefix):
    @wraps(_get_media_root)
    def media_file_name(instance, filename):
        h = str(instance.pk).zfill(10)
        basename, ext = os.path.splitext(filename)
        return os.path.join('mediafiles', prefix, h + ext.lower())

    return media_file_name


def profile_media_root(instance, filename):
    return _get_media_root('profile')(instance, filename)


def org_media_root(instance, filename):
    return _get_media_root('org')(instance, filename)


def app_media_root(instance, filename):
    return _get_media_root('app')(instance, filename)


class MediaFileSystemStorage(FileSystemStorage):
    pass


class AvatarFileSystemStorage(MediaFileSystemStorage):
    pass
