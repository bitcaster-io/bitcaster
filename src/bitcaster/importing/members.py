import codecs
import csv
from contextlib import suppress
from typing import Any, Iterable

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.db import transaction

from ..constants import bitcaster
from ..models import Group, Member
from .utils import get_column_mapping, parse_kv


def process_csv_line(row: dict[str, Any], cleaned_names: dict[str, str]) -> dict[str, Any] | None:
    record = {"custom_fields": {}}
    for fname, col_name in cleaned_names.items():
        value = row.get(col_name, "")
        if fname in ["first_name", "last_name", "email"]:
            record[fname] = value
        elif fname.startswith("custom__"):
            key = fname[8:]
            if col_name.endswith("[]"):
                value = row.get(col_name, "")
                if "[" in value or "{" in value:
                    raise NotImplementedError("Nested structure not supported")
                record["custom_fields"][col_name[8:-2]] = [v.strip() for v in value.split(",") if v.strip()]
            elif col_name.endswith("{}"):
                value = row.get(col_name, "")
                if "[" in value or "{" in value:
                    raise NotImplementedError("Nested structure not supported")
                record["custom_fields"][col_name[8:-2]] = parse_kv(value)
            else:
                record["custom_fields"][key] = value
        else:
            raise NotImplementedError(f"Invalid column name '{col_name}'")
    record["username"] = record["email"]
    return record


def import_members_csv(f: Iterable[bytes], group: "Group|None" = None) -> tuple[int, int]:
    reader = csv.DictReader(codecs.iterdecode(f, "utf-8"))
    if not reader.fieldnames:
        raise NotImplementedError("No fieldnames found")
    cleaned_names = get_column_mapping(reader.fieldnames)
    validator = EmailValidator()
    data = []
    processed = 0
    emails_to_add = []

    for row in reader:
        processed += 1
        email = row.get(cleaned_names.get("email", "email"), "")
        if not email:
            continue
        with suppress(ValidationError):
            validator(email)
            if record := process_csv_line(row, cleaned_names):
                data.append(Member(**record))
                emails_to_add.append(email)

    with transaction.atomic():
        created_count = len(Member.objects.bulk_create(data, ignore_conflicts=True))
        if emails_to_add:
            bitcaster.local_organization.enroll_users(Member.objects.filter(email__in=emails_to_add), group)

    return created_count, processed
