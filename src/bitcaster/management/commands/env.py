from typing import TYPE_CHECKING

from django.core.management import BaseCommand, CommandError, CommandParser

if TYPE_CHECKING:
    from typing import Any

DEVELOP = {
    "DEBUG": True,
    "SECRET_KEY": "only-development-secret-key",
}


class Command(BaseCommand):
    requires_migrations_checks = False
    requires_system_checks = []

    def add_arguments(self, parser: "CommandParser") -> None:
        parser.add_argument(
            "--pattern",
            action="store",
            dest="pattern",
            default="{key}={value}",
            help="Pattern to use to print variables (default: '{key}={value}{space}",
        )
        parser.add_argument("--develop", action="store_true", help="Display development values")
        parser.add_argument("--config", action="store_true", help="Only list changed values")
        parser.add_argument("--diff", action="store_true", help="Mark changed values")
        parser.add_argument(
            "--check", action="store_true", dest="check", default=False, help="Check env for variable availability"
        )
        parser.add_argument(
            "--ignore-errors", action="store_true", dest="ignore_errors", default=False, help="Do not fail"
        )

    def handle(self, *args: "Any", **options: "Any") -> None:
        from bitcaster.config import CONFIG, EXPLICIT_SET, env

        check_failure = False
        pattern = options["pattern"]
        errors = []

        for k, __ in sorted(CONFIG.items()):
            help: str = env.get_help(k)
            default = env.get_default(k)
            if options["check"]:
                if k in EXPLICIT_SET and k not in env.ENVIRON:
                    self.stderr.write(self.style.ERROR(f"- Missing env variable: {k}"))
                    check_failure = True
            else:
                value: Any
                if options["develop"]:
                    value = env.for_develop(k)
                else:
                    try:
                        value = env.get_value(k)
                    except ValueError:
                        errors.append(k)
                        check_failure = True

                line: str = pattern.format(key=k, value=str(value or ""), help=help, default=default, space=" ")
                if options["diff"]:
                    if value != default:
                        line = self.style.SUCCESS(line)
                elif options["config"] and value == default and k not in EXPLICIT_SET:
                    continue
                self.stdout.write(line)

        if check_failure and not options["ignore_errors"]:
            raise CommandError("Env check command failure on following variables: " + ", ".join(errors))
