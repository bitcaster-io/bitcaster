# -*- coding: utf-8 -*-
import sys
import time

import click
from django.db import OperationalError, connections


@click.command(name='check-ready')
@click.pass_context
def isready(self, *args, **options):
    conn = connections[options['connection']]
    elapsed = 0
    retcode = 1
    try:
        self.stdout.write(f"Checking connnection {options['connection']}...")

        while True:
            try:
                conn = self._get_cursor(conn)
            except OperationalError as e:
                if options['wait'] and elapsed < options['timeout']:
                    self.stdout.write('.' * elapsed, ending='\r')
                    self.stdout.flush()
                    time.sleep(options['sleep'])
                    elapsed += 1
                else:
                    self.stderr.write(f"\nDatabase on {conn.settings_dict['HOST']}:{conn.settings_dict['PORT']} "
                                      f'is not available after {elapsed} secs')
                    if options['debug']:
                        self.stderr.write(f'Error is: {e}')
                    retcode = 1
                    break
            else:
                self.stdout.write(f"Connection {options['connection']} successful")
                retcode = 0
                break
    except KeyboardInterrupt:  # pragma: no-cover
        self.stdout.write('Interrupted')
    sys.exit(retcode)
