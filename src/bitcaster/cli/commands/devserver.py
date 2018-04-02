# -*- coding: utf-8 -*-
import logging
import os
import subprocess
import sys
import time
from pathlib import Path

import _thread
import click

from bitcaster.cli import global_options
from bitcaster.cli.utils import Address, LogLevelParamType
from bitcaster.services.http import HTTPServer

logger = logging.getLogger(__name__)

_mtimes = {}
_win = (sys.platform == "win32")
_cached_filenames = []

I18N_MODIFIED = 80
RUN_RELOADER = True
ASSET_MODIFIED = 90
HTML_MODIFIED = 91
SOURCE_MODIFIED = 92
IMAGES = ('.png', '.ico')
JS = ('.js', '.jsx')
PAGES = ('.html', '.html')
SOURCE = ('.py',)
I18N = ('.mo',)

MONITOR_FILES = IMAGES + PAGES + I18N + JS


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def gen_filenames(only_new=False):
    # from django.conf import settings
    # from django.apps import apps
    # from django.core.management import execute_from_command_line
    # from django.utils.autoreload import (I18N_MODIFIED, RUN_RELOADER,
    #                                      ensure_echo_on, reset_translations,)

    global _cached_filenames
    from bitcaster.config.settings import default as settings
    new_filenames = []
    for root, subdirs, files in os.walk(settings.SOURCE_DIR):
        for filename in files:
            __, ext = os.path.splitext(filename)
            if ext in MONITOR_FILES:
                new_filenames.append(os.path.join(root, filename))

    # if not _cached_filenames and settings.USE_I18N:
    #     # Add the names of the .mo files that can be generated
    #     # by compilemessages management command to the list of files watched.
    #     basedirs = [os.path.join(os.path.dirname(os.path.dirname(__file__)),
    #                              'conf', 'locale'),
    #                 'locale']
    #     # for app_config in reversed(list(apps.get_app_configs())):
    #     #     basedirs.append(os.path.join(app_config.path, 'locale'))
    #     basedirs.extend(settings.LOCALE_PATHS)
    #     basedirs = [os.path.abspath(basedir) for basedir in basedirs
    #                 if os.path.isdir(basedir)]
    #     for basedir in basedirs:
    #         for dirpath, dirnames, locale_filenames in os.walk(basedir):
    #             for filename in locale_filenames:
    #                 if filename.endswith('.mo'):
    #                     new_filenames.append(os.path.join(dirpath, filename))
    #
    # # _cached_modules = _cached_modules.union(new_modules)
    _cached_filenames += new_filenames
    if only_new:
        return new_filenames
    else:
        return _cached_filenames


def code_changed():
    global _mtimes, _win
    for filename in gen_filenames():
        stat = os.stat(filename)
        mtime = stat.st_mtime
        if _win:
            mtime -= stat.st_ctime
        if filename not in _mtimes:
            _mtimes[filename] = mtime
            continue
        if mtime != _mtimes[filename]:
            _mtimes = {}
            __, ext = os.path.splitext(filename)
            if ext == '.mo':
                return I18N_MODIFIED
            elif ext in ('.html',):
                return HTML_MODIFIED
            elif ext in ('.py',):
                return SOURCE_MODIFIED
            elif ext in ('.css', '.scss', '.js', 'png', '.jpg'):
                return ASSET_MODIFIED

    return False


def monitor(fn=code_changed, stdout=None, stderr=None):
    # from django.core.management import execute_from_command_line
    # from django.utils.autoreload import reset_translations

    # ensure_echo_on()
    # if USE_INOTIFY:
    #     fn = inotify_code_changed
    # else:
    # TODO: implement inotify. See django.utils.autoreload
    # fn = code_changed
    while RUN_RELOADER:
        change = fn()
        if change == SOURCE_MODIFIED:
            # this is handle by gunicorn
            # sys.exit(3)  # force reload
            pass
        elif change == HTML_MODIFIED:
            touch(Path(__file__).absolute())
        elif change == ASSET_MODIFIED:
            from django.core.management import execute_from_command_line
            stdout.write("Asset change detected run webpack/collectstatic\n")
            subprocess.check_call(['webpack', '--mode', 'development'],
                                  stdout=stdout,
                                  stderr=stderr)
            execute_from_command_line(argv=['manage', 'collectstatic', '--noinput'])

        elif change == I18N_MODIFIED:
            from django.utils.autoreload import reset_translations
            reset_translations()
        time.sleep(1)


@click.command()
@global_options
@click.option('--bind', '-b', default='localhost:8000', type=Address,
              help='Bind address.')
@click.option('--workers', '-w', default=1,
              help='The number of worker processes for handling requests.')
@click.option('--pdb', 'use_pdb', default=False, is_flag=True,
              help='')
@click.option('--debug', '-d', default=False, is_flag=True,
              help='Start server in debug mode')
@click.option('--webpack', default=False, is_flag=True,
              help='Start webpack watch mode')
@click.option('--no-input', default=False, is_flag=True,
              help='Do not prompt the user for input of any kind.')
@click.option('--autoreload/--noreload/', default=True, is_flag=True,
              help='Restart server on server change')
@click.option('--loglevel', '-l', default='debug',
              type=LogLevelParamType(),
              help=('Logging level, choose between DEBUG, INFO, WARNING,'
                    ' ERROR, CRITICAL, or FATAL.'))
@click.option('--logfile', default=None,
              help='logfile')
@click.option('--pidfile', '-p', default=None,
              help='pid filename ')
@click.pass_context
def devserver(ctx, bind, workers, autoreload, debug, pidfile, verbose,
              webpack, use_pdb, logfile, **kwargs):
    host, port = bind.split(":")

    if debug:
        os.environ['BITCASTER_DEBUG'] = 'True'
        os.environ['BITCASTER_CELERY_TASK_ALWAYS_EAGER'] = 'True'

    if webpack:
        _thread.start_new_thread(monitor, ())

    # if use_pdb:
    #     from django.views import debug
    #     debug.technical_500_response = reraise
    if verbose > 0:
        click.echo(f"Starting Bitcaster server on {bind}")

    HTTPServer(host=host,
               port=port,
               debug=debug,
               workers=workers,
               pidfile=pidfile,
               reload=autoreload).run()
