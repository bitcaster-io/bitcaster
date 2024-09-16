import csv
from typing import Any

from django.core.files import File

from bitcaster.models import Group, Organization, User, UserRole


def import_users_to_org(f: File[Any], org: Organization, group: Group, config: dict[str, Any]) -> None:
    data_set = f.read().decode("utf-8-sig").splitlines()
    reader = csv.DictReader(data_set, **config)
    for row in reader:
        user, __ = User.objects.get_or_create(
            username=row["email"], email=row["email"], first_name=row["first_name"], last_name=row["last_name"]
        )
        UserRole.objects.get_or_create(user=user, organization=org, group=group)
