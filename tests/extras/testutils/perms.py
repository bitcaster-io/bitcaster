import contextlib
from contextlib import ContextDecorator
from random import choice
from typing import TYPE_CHECKING, Any, Generator, Iterable, Optional, Union
from unittest.mock import Mock

from django.contrib.auth.models import Permission
from faker import Faker
from testutils.factories.django_auth import GroupFactory

from bitcaster.auth.constants import Grant
from bitcaster.models import ApiKey, Application, Organization, Project, User
from bitcaster.state import state

whitespace = " \t\n\r\v\f"
lowercase = "abcdefghijklmnopqrstuvwxyz"
uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
letters = lowercase + uppercase
ascii_lowercase = lowercase
ascii_uppercase = uppercase
ascii_letters = ascii_lowercase + ascii_uppercase

if TYPE_CHECKING:
    from django.contrib.auth.models import Group

    from bitcaster.models.mixins import LockMixin


class Null:
    def __repr__(self) -> str:
        return "<Null>"


faker = Faker()
keep_existing = Null()


def text(length: int, choices: str = ascii_letters) -> str:
    """returns a random (fixed length) string

    :param length: string length
    :param choices: string containing all the chars can be used to build the string

    .. seealso::
       :py:func:`rtext`
    """
    return "".join(choice(choices) for x in range(length))


def get_group(
    name: Optional[str] = None, permissions: Optional[list[str]] = None, raise_if_missing: bool = True
) -> "Group":
    group = GroupFactory(name=(name or text(5)))
    permission_names = permissions or []
    for permission_name in permission_names:
        try:
            app_label, codename = permission_name.split(".")
        except ValueError:
            raise ValueError(f"Invalid permission name `{permission_name}`")
        try:
            permission = Permission.objects.get(content_type__app_label=app_label, codename=codename)
        except Permission.DoesNotExist:
            if raise_if_missing:
                raise Permission.DoesNotExist("Permission `{0}` does not exists", permission_name)
            else:
                permission = None
        if permission:
            group.permissions.add(permission)
    return group


class set_current_user(ContextDecorator):  # noqa
    def __init__(self, user: "User"):
        self.user = user

    def __enter__(self) -> None:
        r = Mock()
        r.user = self.user
        self.state = state.set(request=r)
        self.state.__enter__()

    def __exit__(self, e_typ: Optional[type], e_val: Optional[Exception], trcbak: Optional[Any]) -> None:
        self.state.__exit__(e_typ, e_val, trcbak)
        if e_typ:
            raise e_typ(e_val).with_traceback(trcbak)


class user_grant_permissions(ContextDecorator):  # noqa
    caches = [
        "_group_perm_cache",
        "_user_perm_cache",
        "_dsspermissionchecker",
        "_officepermissionchecker",
        "_perm_cache",
        "_dss_acl_cache",
    ]

    def __init__(
        self,
        user: "User",
        permissions: Optional[list[str]] = None,
        group_name: Optional[str | None] = None,
        ignore_missing: bool = False,
    ) -> None:
        self.user = user
        if permissions and not isinstance(permissions, (list, tuple)):
            permissions = [permissions]
        self.permissions = permissions
        self.group_name = group_name
        self.group: "Optional[Group]" = None
        self.ignore_missing = ignore_missing
        self._groups = user.groups.all()

    def __enter__(self) -> "user_grant_permissions":
        for cache in self.caches:
            if hasattr(self.user, cache):
                delattr(self.user, cache)

        self.group = get_group(
            name=self.group_name, permissions=self.permissions or [], raise_if_missing=not self.ignore_missing
        )
        self.user.groups.clear()
        self.user.groups.add(self.group)
        return self

    def __exit__(self, e_typ: Optional[type], e_val: Optional[Exception], trcbak: Optional[Any]) -> None:
        if self.group:
            self.user.groups.remove(self.group)
            self.group.delete()
        for g in self._groups:
            self.user.groups.add(g)

        if e_val:
            raise e_val.with_traceback(trcbak)

    def start(self) -> "user_grant_permissions":
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self) -> None:
        """Stop an active patch."""
        return self.__exit__(None, None, None)


@contextlib.contextmanager
def lock(target: "LockMixin") -> "Generator[None, None, None]":
    value: bool = target.locked
    if not value:
        target.locked = True
        target.save()
    yield
    if not value:
        target.locked = False
        target.save()


class key_grants(ContextDecorator):  # noqa
    caches: list[Any] = []

    def __init__(
        self,
        key: "ApiKey",
        grants: Optional[Grant | list[Grant | None] | None] = None,
        add: bool = True,
        organization: "Union[Null, None, Organization]" = keep_existing,
        project: "Union[Null, None, Project]" = keep_existing,
        application: "Union[Null, None, Application]" = keep_existing,
        environments: "Union[Null, Iterable[str]]" = keep_existing,
    ):
        self.key = key
        if not isinstance(grants, (list, tuple)):
            grants = [grants]
        # self.new_grants = grants
        self.add = add
        if organization is None:
            project = None

        if project is None:
            application = None
        if application and isinstance(application, Application):
            project = application.project
        if project and project != keep_existing:
            organization = project.organization

        self.state = {
            "grants": self.key.grants,
            "organization": self.key.organization,
            "project": self.key.project,
            "application": self.key.application,
            "environments": self.key.environments,
        }
        self.new_state = {
            "grants": grants,
            "organization": key.organization if organization is keep_existing else organization,
            "project": key.project if project is keep_existing else project,
            "application": key.application if application is keep_existing else application,
            "environments": key.environments if environments is keep_existing else environments,
        }

    def __enter__(self) -> "key_grants":
        if self.add:
            self.key.grants.extend(self.new_state["grants"])
        else:
            self.key.grants = self.new_state["grants"]
        self.key.organization = self.new_state["organization"]
        self.key.project = self.new_state["project"]
        self.key.application = self.new_state["application"]
        self.key.environments = self.new_state["environments"]

        self.key.save()
        return self

    def __exit__(self, e_typ: Optional[type], e_val: Optional[Exception], trcbak: Optional[Any]) -> None:
        self.key.grants = self.state["grants"]
        self.key.organization = self.state["organization"]
        self.key.project = self.state["project"]
        self.key.application = self.state["application"]
        self.key.environments = self.state["environments"]
        self.key.save()

        if e_val:
            raise e_val.with_traceback(trcbak)

    def start(self) -> "key_grants":
        """Activate a patch, returning any created mock."""
        result = self.__enter__()
        return result

    def stop(self) -> None:
        """Stop an active patch."""
        return self.__exit__(None, None, None)
