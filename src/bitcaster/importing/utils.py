import shlex
from ast import literal_eval
from typing import Sequence

from django.utils.text import slugify


def get_column_mapping(headers: Sequence[str]) -> dict[str, str]:
    return {slugify(f.strip()).replace("-", "_"): f for f in headers}


def parse_kv(value: str) -> dict[str, object]:
    lexer = shlex.shlex(value, posix=True)
    lexer.whitespace = ","
    lexer.whitespace_split = True
    lexer.commenters = ""

    result: dict[str, object] = {}

    for token in lexer:
        if "=" not in token:
            continue

        key, raw = token.split("=", 1)

        try:
            result[key.strip()] = literal_eval(raw)
        except Exception:
            result[key.strip()] = raw

    return result
