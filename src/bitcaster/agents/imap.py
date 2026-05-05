from typing import Any

import imaplib
import logging
import re
from email import policy
from email.message import EmailMessage, Message
from email.parser import BytesParser

from django import forms
from django.utils.translation import gettext_lazy as _

from .base import Agent, AgentConfig

logger = logging.getLogger(__name__)


class AgentImapConfig(AgentConfig):
    server = forms.CharField(label=_("IMAP Server"), help_text=_("IMAP server hostname"))
    port = forms.IntegerField(label=_("Port"), initial=993, help_text=_("IMAP port (993 for SSL)"))
    username = forms.CharField(label=_("Username"), help_text=_("IMAP account username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput, help_text=_("IMAP account password"))
    use_ssl = forms.BooleanField(label=_("Use SSL"), initial=True, required=False)
    folder = forms.CharField(label=_("Folder"), initial="INBOX", help_text=_("Mailbox folder to monitor"))
    subject_pattern = forms.CharField(
        label=_("Subject pattern"),
        help_text=_("Regex with named groups to extract fields from subject (e.g. r'Alert: (?P<alert_type>\\w+)')"),
    )
    body_pattern = forms.CharField(
        label=_("Body pattern"),
        required=False,
        help_text=_("Optional regex with named groups to extract fields from body"),
    )

    def clean_subject_pattern(self) -> str:
        try:
            re.compile(self.cleaned_data["subject_pattern"])
        except re.error as e:
            raise forms.ValidationError(_("Invalid regex: %(error)s") % {"error": e}) from e
        return self.cleaned_data["subject_pattern"]

    def clean_body_pattern(self) -> str:
        if self.cleaned_data.get("body_pattern"):
            try:
                re.compile(self.cleaned_data["body_pattern"])
            except re.error as e:
                raise forms.ValidationError(_("Invalid regex: %(error)s") % {"error": e}) from e
        return self.cleaned_data["body_pattern"]


class AgentImap(Agent):
    config_class: type[AgentImapConfig] = AgentImapConfig

    def connect(self) -> imaplib.IMAP4_SSL | imaplib.IMAP4:
        cfg = self.config
        if cfg["use_ssl"]:
            return imaplib.IMAP4_SSL(cfg["server"], cfg["port"])
        return imaplib.IMAP4(cfg["server"], cfg["port"])

    def fetch_unseen(self, client: imaplib.IMAP4_SSL | imaplib.IMAP4) -> list[tuple[str, EmailMessage]]:
        cfg = self.config
        client.login(cfg["username"], cfg["password"])
        client.select(cfg["folder"])
        status, messages = client.search(None, "UNSEEN")
        if status != "OK" or not messages[0]:
            return []
        email_ids: list[bytes] = messages[0].split()
        results: list[tuple[str, EmailMessage]] = []
        for eid in email_ids:
            status, msg_data = client.fetch(eid.decode(), "(RFC822)")
            if status == "OK" and msg_data:
                data = msg_data[0]
                if isinstance(data, tuple) and len(data) > 1:
                    raw = data[1]
                    if isinstance(raw, bytes):
                        msg = self._parse_email(raw)
                        if msg:
                            results.append((eid.decode(), msg))
        return results

    def _parse_email(self, raw: bytes) -> EmailMessage | None:
        try:
            msg = BytesParser(policy=policy.default).parsebytes(raw)
            if isinstance(msg, EmailMessage) and msg.get("Subject") is not None:
                return msg
        except Exception as e:
            logger.error(e)
        return None

    def extract_fields(self, msg: Message) -> dict[str, Any] | None:
        cfg = self.config
        subject_val = msg.get("Subject")
        subject = subject_val if isinstance(subject_val, str) else ""
        subject_pattern = cfg["subject_pattern"]
        match = re.search(subject_pattern, subject)
        if not match:
            return None
        fields: dict[str, Any] = match.groupdict()
        body_pattern = cfg.get("body_pattern")
        if body_pattern:
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        content = part.get_content()
                        if isinstance(content, str):
                            body = content
                        break
            else:
                content = msg.get_content()
                if isinstance(content, str):
                    body = content
            body_match = re.search(body_pattern, body)
            if body_match:
                fields.update(body_match.groupdict())
        fields["subject"] = subject
        from_val = msg.get("From")
        fields["from"] = from_val if isinstance(from_val, str) else ""
        date_val = msg.get("Date")
        fields["date"] = date_val if isinstance(date_val, str) else ""
        return fields

    def check(self, notify: bool = True, update: bool = True) -> None:
        stored_ids = set(self.monitor.data.get("processed_ids", []))
        client = self.connect()
        try:
            emails = self.fetch_unseen(client)
            matches: list[dict[str, Any]] = []
            for eid, msg in emails:
                if eid in stored_ids:
                    continue
                fields = self.extract_fields(msg)
                if fields:
                    matches.append({"id": eid, "fields": fields})
                    stored_ids.add(eid)
            self.monitor.data = {
                "processed_ids": list(stored_ids),
                "last_check": self.monitor.data.get("last_check", ""),
            }
            if update:
                self.monitor.save()
            if notify and matches:
                for match in matches:
                    fields = match["fields"]
                    if isinstance(fields, dict):
                        self.monitor.event.trigger(context=fields)
        finally:
            try:
                client.logout()
            except Exception as e:
                logger.error(e)

    def changes_detected(self) -> bool:
        stored_ids = set(self.monitor.data.get("processed_ids", []))
        client = self.connect()
        try:
            emails = self.fetch_unseen(client)
            for eid, msg in emails:
                if eid in stored_ids:
                    continue
                if self.extract_fields(msg):
                    return True
        finally:
            try:
                client.logout()
            except Exception as e:
                logger.error(e)
        return False

    def notify(self) -> None:
        self.check(notify=True, update=False)
