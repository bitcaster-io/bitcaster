from cron_descriptor import (
    FormatException,
    MissingFieldException,
    WrongArgumentException,
    get_description,
)


def human_readable(cron_expression: str) -> str:
    try:
        readable = get_description(cron_expression)
    except (MissingFieldException, FormatException, WrongArgumentException):
        return f"{cron_expression}"
    return f"{readable}"
