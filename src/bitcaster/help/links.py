from typing import Final

import re

HELP_LINKS: Final[dict[str, str]] = {
    "^/admin/$": "adm-guide/quickstart/",
    "^/admin/bitcaster/applicationmembership": "adm-guide/membership/",
    "^/admin/bitcaster/application": "adm-guide/app/",
    "^/admin/bitcaster/event": "adm-guide/events/",
    "^/admin/bitcaster/eventsimulation": "adm-guide/events/",
    "^/admin/bitcaster/deliverysimulation": "adm-guide/events/",
    "^/admin/bitcaster/notification": "adm-guide/notification/",
    "^/admin/bitcaster/messagetemplate": "adm-guide/message/",
    "^/admin/bitcaster/channel": "adm-guide/abstract_channel_create/",
    "^/admin/bitcaster/monitor": "adm-guide/monitor/",
    "^/admin/bitcaster/apikey": "adm-guide/api_key/",
    "^/admin/bitcaster/distributionlist": "adm-guide/dl/",
    "^/admin/bitcaster/user": "adm-guide/user_management/",
    "^/admin/bitcaster/userrole": "adm-guide/user_management/",
    "^/admin/bitcaster/usermessage": "adm-guide/dispatchers/user_message/",
    "^/admin/bitcaster/organization": "adm-guide/structure/",
    "^/admin/bitcaster/project": "adm-guide/structure/",
    "^/admin/bitcaster/assignment": "adm-guide/notification_policies/",
    "^/admin/bitcaster/occurrence": "adm-guide/occurrence/",
    "^/admin/bitcaster/member": "adm-guide/member/",
    "^/admin/bitcaster/subscription": "adm-guide/subscription/",
    "^/admin/bitcaster/address": "adm-guide/address/",
    "^/admin/bitcaster/attachment": "adm-guide/attachment/",
    "^/admin/bitcaster/mediafile": "adm-guide/media/",
    "^/admin/bitcaster/logmessage": "adm-guide/stream/",
    "^/admin/bitcaster/processlogentry": "adm-guide/process_log/",
    "^/admin/bitcaster/task": "adm-guide/tasks/",
    "^/admin/bitcaster/logentry": "adm-guide/system_log/",
    "^/admin/bitcaster/delivery": "adm-guide/occurrence/",
    "^/admin/flags/flagstate": "adm-guide/flags/",
    "^/admin/constance/config": "configuration/",
    "^/admin/auth/group": "adm-guide/user_management/",
    "^/admin/social/": "adm-guide/sso/",
    "^/admin/webpush/": "adm-guide/address/",
    "^/admin/": "adm-guide/quickstart/",
    "^/console/": "adm-guide/cli/",
}

_COMPILED: Final[list[tuple[re.Pattern[str], str]]] = [
    (re.compile(pattern), doc_path) for pattern, doc_path in HELP_LINKS.items()
]


def resolve_help_path(path: str) -> str | None:
    best: tuple[int, int, int] | None = None
    result: str | None = None
    for idx, (pattern, doc_path) in enumerate(_COMPILED):
        match = pattern.match(path)
        if match is None:
            continue
        candidate = (len(match.group(0)), len(pattern.pattern), -idx)
        if best is None or candidate > best:
            best = candidate
            result = doc_path
    return result


def resolve_help_url(path: str, doc_site: str) -> str | None:
    doc_path = resolve_help_path(path)
    if doc_path is None or not doc_site:
        return None
    return f"{doc_site.rstrip('/')}/{doc_path}"
