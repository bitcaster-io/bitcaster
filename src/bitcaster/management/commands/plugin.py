import re
import sys
from pathlib import Path

from cookiecutter.generate import generate_files
from django.core.management.base import BaseCommand

import bitcaster

name_char_blacklist_regexp = re.compile('[a-z-]*\d*$')


def is_valid_name(name):
    return name_char_blacklist_regexp.match(name)


def cook(input_dir, output_dir, context=None, overwrite=True):
    generate_files(
        repo_dir=input_dir,
        context=context,
        output_dir=output_dir,
        overwrite_if_exists=overwrite
    )


class Command(BaseCommand):
    help = "My shiny new management command."
    requires_system_checks = False
    requires_migrations_checks = False

    def add_arguments(self, parser):
        parser.add_argument('name', action='store')
        parser.add_argument('--new', action='store_true')
        parser.add_argument('--overwrite', '-o', action='store_true')
        parser.add_argument('-d', action='store',
                            default=str(Path(bitcaster.__file__).parent.parent.parent / 'plugins'),
                            dest='directory')
        parser.add_argument('--description', action='store')

    def handle(self, *args, **options):
        name = options['name'].lower()
        directory = options['directory']
        description = options['description']
        if not is_valid_name(name):
            self.stderr.write("Invalid package name %s" % name)
            sys.exit(1)
        base_dir = Path(bitcaster.__file__).parent / '_plugin_template'
        name = str(name).lower()
        package_name = "bitcaster_" + name.lower().replace('-', '_')
        classname = str(name).title().replace('-', '').replace('Oauth', 'OAuth')

        context = {'cookiecutter': {'name': name,
                                    'package_name': package_name,
                                    'classname': classname,
                                    'description': description}
                   }
        cook(str(base_dir), directory, context, overwrite=options['overwrite'])

        self.stdout.write('%s application was succesfully created.' % name)
        self.stdout.write(directory)
