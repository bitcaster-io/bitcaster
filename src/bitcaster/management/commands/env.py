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
            default="{key}={value}  # {help}",
            help="Check env for variable availability (default: '{key}={value}  # {help}')",
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
        from bitcaster.config import CONFIG, env, EXPLICIT_SET

        check_failure = False
        pattern = options["pattern"]

        for k, __ in sorted(CONFIG.items()):
            help: str = env.get_help(k)
            default = env.get_default(k)
            if options["check"]:
                if k in EXPLICIT_SET and k not in env.ENVIRON:
                    self.stderr.write(self.style.ERROR(f"- Missing env variable: {k}"))
                    check_failure = True
            else:
                if options["develop"]:
                    value: Any = env.for_develop(k)
                else:
                    value: Any = env.get_value(k)

                line: str = pattern.format(key=k, value=value, help=help, default=default)
                if options["diff"]:
                    if value != default:
                        line = self.style.SUCCESS(line)
                elif options["config"]:
                    if value == default and k not in EXPLICIT_SET:
                        continue
                self.stdout.write(line)

        if check_failure and not options["ignore_errors"]:
            raise CommandError("Env check command failure!")
