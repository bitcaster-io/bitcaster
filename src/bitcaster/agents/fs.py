from functools import cached_property
from pathlib import Path
from typing import Any

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.module_loading import import_string
from django.utils.translation import gettext as _

from .base import Agent, AgentConfig


def _validate_path(path: str) -> None:
    if callable(settings.AGENT_FILESYSTEM_VALIDATOR):
        f = settings.AGENT_FILESYSTEM_VALIDATOR
    else:
        f = import_string(settings.AGENT_FILESYSTEM_VALIDATOR)
    try:
        f(path)
    except ValidationError as e:
        raise e
    except Exception as e:
        raise ValidationError("Invalid Path") from e


def resolve_path(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    if settings.AGENT_FILESYSTEM_ROOT and not path.startswith(settings.AGENT_FILESYSTEM_ROOT):
        path = settings.AGENT_FILESYSTEM_ROOT + path
    return str(Path(path).resolve().absolute())


def validate_path(path: str) -> bool:
    p = Path(resolve_path(path))
    if settings.AGENT_FILESYSTEM_ROOT:
        if Path(settings.AGENT_FILESYSTEM_ROOT) not in p.parents and Path(settings.AGENT_FILESYSTEM_ROOT) != p:
            raise ValidationError(
                _(
                    "Path '%(path)s' is outside allowed root: '%(root)s'"
                    % {"path": p, "root": settings.AGENT_FILESYSTEM_ROOT}
                )
            )
    return True


class AgentFileSystemConfig(AgentConfig):
    path = forms.CharField(widget=forms.TextInput(attrs={"class": "path"}))
    recursive = forms.BooleanField(help_text=_("Check also subdirectories"), required=False)
    add = forms.BooleanField(help_text=_("Monitor directory for new files"), required=False)
    change = forms.BooleanField(help_text=_("Monitor directory for changed files"), required=False)
    delete = forms.BooleanField(help_text=_("Monitor directory for deleted files"), required=False)

    def clean_path(self) -> str:
        _validate_path(self.cleaned_data["path"])
        return self.cleaned_data["path"]


class AgentFiles(Agent):
    config_class: type[AgentConfig] = AgentFileSystemConfig
    abstract = True

    def initialize(self) -> None:
        entries = self.scan()
        self.monitor.data = {
            "entries": entries,
            "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "diff": {"changed": [], "added": [], "deleted": []},
        }
        self.monitor.save()

    @cached_property
    def path(self) -> Path:
        return Path(self.config["path"])

    def diff(self, stored: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
        ret = {"changed": [], "added": [], "deleted": []}
        for entry, data in current.items():
            if entry not in stored:
                ret["added"].append(entry)
            elif data != stored[entry]:
                ret["changed"].append(entry)
        for key in stored:
            if key not in current:
                ret["deleted"].append(key)
        return ret

    def scan(self) -> dict[str, Any]:
        raise NotImplementedError

    def check(self, notify: bool = True, update: bool = True) -> None:
        if not self.monitor.data:
            self.initialize()
            return
        status = self.monitor.data.get("entries", [])
        current = self.scan()
        diff = self.diff(status, current)
        self.monitor.data = {
            "entries": current,
            "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "diff": diff,
        }
        if update:
            self.monitor.save()
        if (
            notify
            and (self.config["change"] and self.monitor.data["diff"]["changed"])
            or (self.config["delete"] and self.monitor.data["diff"]["deleted"])
            or (self.config["add"] and self.monitor.data["diff"]["added"])
        ):
            self.notify()

    def changes_detected(self) -> bool:
        return any(self.monitor.data["diff"][k] for k in ["changed", "added", "deleted"])

    def notify(self) -> None:
        self.monitor.event.trigger(context=self.monitor.data)


class AgentFileSystem(AgentFiles):
    config_class: type[AgentFileSystemConfig] = AgentFileSystemConfig

    def scan(self) -> dict[str, Any]:
        entries = {}
        if self.path.is_dir():
            if self.config["recursive"]:
                for root, _dirs, files in self.path.walk():
                    for f in files:
                        entries[str(Path(root / f).absolute())] = str(Path(root / f).stat().st_atime)
            else:
                for f in self.path.iterdir():  # type: ignore[assignment]
                    entries[str(f.absolute())] = str(f.stat().st_atime)
        elif self.path.is_file():
            entries[str(self.path.absolute())] = str(self.path.stat().st_atime)
        return entries

    #
    # def initialize(self) -> None:
    #     entries = self.scan()
    #     self.monitor.data = {
    #         "entries": entries,
    #         "timestamp": timezone.now().strftime("%Y%m%d%H%M%S"),
    #         "diff": {"changed": [], "added": [], "deleted": []},
    #         "changed": False,
    #     }
    #     self.monitor.save()
    #
    # @cached_property
    # def path(self) -> Path:
    #     return Path(self.config["path"])
    #
    # def diff(self, stored: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    #     ret = {"changed": [], "added": [], "deleted": []}
    #     for entry, data in current.items():
    #         if entry not in stored.keys():
    #             ret["added"].append(entry)
    #         elif data != stored[entry]:
    #             ret["changed"].append(entry)
    #     for key, __ in stored.items():
    #         if key not in current.keys():
    #             ret["deleted"].append(key)
    #     return ret
    #
    # def scan(self) -> dict[str, Any]:
    #     entries = {}
    #     if self.path.is_dir():
    #         if self.config["recursive"]:
    #             for root, dirs, files in self.path.walk():
    #                 for f in files:
    #                     entries[str(Path(root / f).absolute())] = str(Path(root / f).stat().st_atime)
    #         else:
    #             for f in self.path.iterdir():  # type: ignore[assignment]
    #                 entries[str(f.absolute())] = str(f.stat().st_atime)
    #     elif self.path.is_file():
    #         entries[str(self.path.absolute())] = str(self.path.stat().st_atime)
    #     return entries
    #
    # def check(self, notify: bool = True, update: bool = True) -> None:
    #     if not self.monitor.data:
    #         self.initialize()
    #         return
    #     status = self.monitor.data["entries"]
    #     current = self.scan()
    #     diff = self.diff(status, current)
    #     self.monitor.data = {
    #         "entries": current,
    #         "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
    #         "diff": diff,
    #         "changed": diff["changed"] or diff["added"] or diff["deleted"],
    #     }
    #     if update:
    #         self.monitor.save()
    #     if (
    #         notify
    #         and (self.config["change"] and self.monitor.data["diff"]["changed"])
    #         or (self.config["delete"] and self.monitor.data["diff"]["deleted"])
    #         or (self.config["add"] and self.monitor.data["diff"]["added"])
    #     ):
    #         self.notify()
    #
    # def notify(self) -> None:
    #     self.monitor.event.trigger(context=self.monitor.data)
