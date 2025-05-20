import ftplib  # nosec
from functools import cached_property
from typing import Any

from django import forms
from django.utils.translation import gettext as _

from .base import AgentConfig
from .fs import AgentFiles


class AgentFTPConfig(AgentConfig):
    server = forms.CharField()
    path = forms.CharField()
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    add = forms.BooleanField(help_text=_("Monitor directory for new files"), required=False)
    change = forms.BooleanField(help_text=_("Monitor directory for changed files"), required=False)
    delete = forms.BooleanField(help_text=_("Monitor directory for deleted files"), required=False)


class AgentFTP(AgentFiles):
    config_class: type[AgentFTPConfig] = AgentFTPConfig

    @cached_property
    def client(self) -> ftplib.FTP:
        f = ftplib.FTP()  # nosec
        host, port = self.config["server"].split(":")
        f.connect(host, int(port))
        f.login(self.config["username"], self.config["password"])
        return f

    def scan(self) -> dict[str, Any]:
        return dict(self.client.mlsd(self.config["path"]))

    #
    # def notify(self) -> None:
    #     self.monitor.event.trigger(context=self.monitor.data)
