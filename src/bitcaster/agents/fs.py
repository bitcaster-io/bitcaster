from functools import cached_property
from pathlib import Path
from typing import Any

from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _

from bitcaster.agents.base import Agent, AgentConfig


class AgentFileSystemConfig(AgentConfig):
    path = forms.CharField(widget=forms.TextInput(attrs={"class": "path"}))
    monitor_add = forms.BooleanField(help_text=_("Monitor directory for new files"), required=False)
    monitor_change = forms.BooleanField(help_text=_("Monitor directory for changed files"), required=False)
    monitor_deletion = forms.BooleanField(help_text=_("Monitor directory for deleted files"), required=False)
    skip_first_run = forms.BooleanField(help_text=_("Skip first run"), required=False)


class AgentFileSystem(Agent):
    config_class: type[AgentFileSystemConfig] = AgentFileSystemConfig

    def initialize(self) -> None:
        entries = self.scan()
        self.monitor.data = {
            "entries": entries,
            "timestamp": timezone.now().strftime("%Y%m%d%H%M%S"),
        }
        self.monitor.save()

    @cached_property
    def path(self) -> Path:
        return Path(self.config["path"])

    def scan(self) -> dict[str, Any]:
        entries = {}
        if self.path.is_dir():
            for root, dirs, files in self.path.walk():
                for f in files:
                    entries[str(Path(root / f).absolute())] = str(Path(root / f).stat().st_atime)
        elif self.path.is_file():
            entries[str(self.path.absolute())] = str(self.path.stat().st_atime)
        return entries

    def check(self) -> None:
        if not self.monitor.data:
            self.initialize()
            return
        status = self.monitor.data["entries"]
        current = self.scan()
        if status != current:
            self.monitor.data = {
                "entries": current,
                "timestamp": timezone.now().strftime("%Y%m%d%H%M%S"),
                "diff": dict(set(status.items()) ^ set(current.items())),
            }
            self.monitor.save()
            self.notify()

    def notify(self) -> None:
        self.config["event"].trigger(context=self.monitor.data)
