# -*- coding: utf-8 -*-
import os
import signal
import sys
import time
from io import StringIO
from pathlib import Path
from unittest.mock import Mock

import _thread
import requests
from click.testing import CliRunner

from bitcaster.cli.commands.devserver import devserver
from bitcaster.config.environ import env


def test_cli_devserver(monkeypatch):
    runner = CliRunner(echo_stdin=True)
    config_file = Path(__file__).parent / 'sample.conf'
    monkeypatch.setitem(os.environ, 'BITCASTER_CONF', str(config_file))
    env.load_config(str(config_file))

    def ping(stdout):
        while True:
            try:
                requests.get('http://localhost:8888')
                break
            except Exception:
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
        pid = open('aaa.pid', 'r').read()
        os.kill(int(pid), signal.SIGTERM)
        _thread.exit()

    _thread.start_new_thread(ping, (sys.stdout,))
    result = runner.invoke(devserver,
                           args=['--bind', 'localhost:8888',
                                 '--webpack',
                                 '-d', '-l', 'debug',
                                 '--pidfile', 'aaa.pid'],
                           obj={'config': os.environ['BITCASTER_CONF']})

    assert result.exit_code == 0, result.output


def test_cli_devserver_monitor(monkeypatch):
    from bitcaster.cli.commands.devserver import (monitor, SOURCE_MODIFIED,
                                                  ASSET_MODIFIED, HTML_MODIFIED,
                                                  I18N_MODIFIED)
    monkeypatch.setattr('bitcaster.cli.commands.devserver.subprocess.check_call', Mock())
    monkeypatch.setattr('django.core.management.execute_from_command_line', Mock())

    def func_factory(ret_value):
        monkeypatch.setattr('bitcaster.cli.commands.devserver.RUN_RELOADER', True)

        def func():
            monkeypatch.setattr('bitcaster.cli.commands.devserver.RUN_RELOADER', False)
            return ret_value

        return func

    out = StringIO()
    err = StringIO()
    monitor(func_factory(SOURCE_MODIFIED), out, err)
    monitor(func_factory(HTML_MODIFIED), out, err)
    monitor(func_factory(ASSET_MODIFIED), out, err)
    monitor(func_factory(I18N_MODIFIED), out, err)
    monitor(func_factory(None))


def test_cli_devserver_code_changed(monkeypatch):
    from bitcaster.cli.commands.devserver import code_changed, touch

    monkeypatch.setattr('bitcaster.cli.commands.devserver.gen_filenames',
                        lambda: [__file__])

    assert not code_changed()
    assert not code_changed()

    touch(__file__)
    assert code_changed()


def test_cli_devserver_code_gen_filenames(monkeypatch):
    from bitcaster.cli.commands.devserver import gen_filenames
    monkeypatch.setattr('bitcaster.cli.commands.devserver.gen_filenames',
                        lambda: [__file__])

    assert gen_filenames()
