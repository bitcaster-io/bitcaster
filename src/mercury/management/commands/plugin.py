import re
import sys
from django.core.management.base import BaseCommand
from pathlib import Path

from cookiecutter.generate import generate_files

import mercury

name_char_blacklist_regexp = re.compile('[a-z]*\d*$')


def is_valid_name(name):
    return name_char_blacklist_regexp.match(name)


def cook(input_dir, output_dir, context=None):
    generate_files(
        repo_dir=input_dir,
        context=context,
        output_dir=output_dir,
    )


class Command(BaseCommand):
    help = "My shiny new management command."
    requires_system_checks = False
    requires_migrations_checks = False

    def add_arguments(self, parser):
        parser.add_argument('name', action='store')
        parser.add_argument('--new', action='store_true')
        parser.add_argument('-d', action='store',
                            default=str(Path(mercury.__file__).parent.parent.parent / 'plugins'),
                            dest='directory')
        parser.add_argument('--description', action='store')

    def handle(self, *args, **options):
        name = options['name'].lower()
        directory = options['directory']
        description = options['description']
        if not is_valid_name(name):
            self.stderr.write("Invalid package name %s" % name)
            sys.exit(1)
        base_dir = Path(mercury.__file__).parent / '_plugin_template'

        context = {'cookiecutter': {'name': str(name).lower(),
                                    'classname': str(name).title(),
                                    'description': description}
                   }
        cook(str(base_dir), directory, context)

        self.stdout.write('%s application was succesfully created.' % name)
        self.stdout.write(directory)
