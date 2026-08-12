# mypy: disable-error-code="attr-defined"

import re

import pytest

from bitcaster.help.links import HELP_LINKS, resolve_help_path, resolve_help_url


@pytest.mark.parametrize(
    "path, expected",
    [
        pytest.param("/admin/", "adm-guide/quickstart/", id="admin-index"),
        pytest.param("/admin/bitcaster/application/", "adm-guide/app/", id="application-changelist"),
        pytest.param("/admin/bitcaster/application/1/change/", "adm-guide/app/", id="application-change"),
        pytest.param("/admin/bitcaster/applicationmembership/", "adm-guide/membership/", id="application-membership"),
        pytest.param("/admin/bitcaster/applicationmembership/1/", "adm-guide/membership/", id="membership-change"),
        pytest.param("/admin/bitcaster/event/", "adm-guide/events/", id="event"),
        pytest.param("/admin/bitcaster/notification/", "adm-guide/notification/", id="notification"),
        pytest.param("/admin/bitcaster/channel/", "adm-guide/abstract_channel_create/", id="channel"),
        pytest.param("/admin/bitcaster/monitor/", "adm-guide/monitor/", id="monitor"),
        pytest.param("/admin/bitcaster/apikey/", "adm-guide/api_key/", id="apikey"),
        pytest.param("/admin/bitcaster/distributionlist/", "adm-guide/dl/", id="distribution"),
        pytest.param("/admin/bitcaster/messagetemplate/", "adm-guide/message/", id="message"),
        pytest.param("/admin/bitcaster/organization/", "adm-guide/structure/", id="organization"),
        pytest.param("/admin/bitcaster/project/", "adm-guide/structure/", id="project"),
        pytest.param("/admin/bitcaster/assignment/", "adm-guide/notification_policies/", id="assignment"),
        pytest.param("/admin/bitcaster/occurrence/", "adm-guide/occurrence/", id="occurrence"),
        pytest.param("/admin/bitcaster/member/", "adm-guide/member/", id="member"),
        pytest.param("/admin/bitcaster/subscription/", "adm-guide/subscription/", id="subscription"),
        pytest.param("/admin/bitcaster/address/", "adm-guide/address/", id="address"),
        pytest.param("/admin/bitcaster/attachment/", "adm-guide/attachment/", id="attachment"),
        pytest.param("/admin/bitcaster/mediafile/", "adm-guide/media/", id="mediafile"),
        pytest.param("/admin/bitcaster/logmessage/", "adm-guide/stream/", id="logmessage"),
        pytest.param("/admin/bitcaster/processlogentry/", "adm-guide/process_log/", id="processlogentry"),
        pytest.param("/admin/bitcaster/task/", "adm-guide/tasks/", id="task"),
        pytest.param("/admin/bitcaster/logentry/", "adm-guide/system_log/", id="logentry"),
        pytest.param("/admin/flags/flagstate/", "adm-guide/flags/", id="flags"),
        pytest.param("/admin/constance/config/", "configuration/", id="constance"),
        pytest.param("/admin/auth/group/", "adm-guide/user_management/", id="group"),
        pytest.param("/admin/bitcaster/whatever/", "adm-guide/quickstart/", id="unmapped-model-fallback"),
        pytest.param("/admin/social/socialaccount/", "adm-guide/sso/", id="social-provider"),
        pytest.param("/admin/webpush/browser/", "adm-guide/address/", id="webpush-browser"),
        pytest.param("/admin/bitcaster/delivery/", "adm-guide/occurrence/", id="delivery"),
        pytest.param("/console/", "adm-guide/cli/", id="console"),
        pytest.param("/console/1/", "adm-guide/cli/", id="console-detail"),
    ],
)
def test_exact_match(path: str, expected: str) -> None:
    assert resolve_help_path(path) == expected


def test_weighted_strictest_wins() -> None:
    assert resolve_help_path("/admin/bitcaster/event/1/change/") == "adm-guide/events/"
    assert resolve_help_path("/admin/bitcaster/event/") == "adm-guide/events/"
    assert resolve_help_path("/admin/") == "adm-guide/quickstart/"


@pytest.mark.parametrize(
    "path, expected",
    [
        pytest.param("/admin/bitcaster/eventsimulation/", "adm-guide/events/", id="eventsimulation"),
        pytest.param("/admin/bitcaster/eventsimulation/1/deliveries/", "adm-guide/events/", id="eventsimulation-sub"),
        pytest.param("/admin/bitcaster/userrole/", "adm-guide/user_management/", id="userrole"),
        pytest.param("/admin/bitcaster/usermessage/", "adm-guide/dispatchers/user_message/", id="usermessage"),
        pytest.param("/admin/bitcaster/user/", "adm-guide/user_management/", id="user"),
        pytest.param("/admin/bitcaster/deliverysimulation/", "adm-guide/events/", id="deliverysimulation"),
        pytest.param("/admin/bitcaster/delivery/", "adm-guide/occurrence/", id="delivery-prefix-wins"),
        pytest.param("/admin/bitcaster/deliverysimulation/1/", "adm-guide/events/", id="delivery-sim-sub-prefix"),
    ],
)
def test_prefix_collisions(path: str, expected: str) -> None:
    assert resolve_help_path(path) == expected


def test_no_match() -> None:
    assert resolve_help_path("/") is None
    assert resolve_help_path("/recipients/abc123/") is None
    assert resolve_help_path("/login/") is None


def test_query_strings_ignored() -> None:
    assert resolve_help_path("/admin/bitcaster/application/?a=1") == "adm-guide/app/"


def test_trailing_slash_handled() -> None:
    assert resolve_help_path("/admin/bitcaster/application") == "adm-guide/app/"
    assert resolve_help_path("/admin/") == "adm-guide/quickstart/"


def test_tie_break_longer_pattern(monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.help import links

    monkeypatch.setattr(
        links,
        "_COMPILED",
        [(re.compile("^/x/"), "short"), (re.compile("^/x/$"), "long")],
    )
    assert resolve_help_path("/x/") == "long"


def test_tie_break_declaration_order(monkeypatch: pytest.MonkeyPatch) -> None:
    from bitcaster.help import links

    monkeypatch.setattr(
        links,
        "_COMPILED",
        [(re.compile("^/x/"), "first"), (re.compile("^/x/"), "second")],
    )
    assert resolve_help_path("/x/anything") == "first"


def test_help_url_join() -> None:
    assert (
        resolve_help_url("/admin/bitcaster/application/", "https://docs.example.com")
        == "https://docs.example.com/adm-guide/app/"
    )
    assert (
        resolve_help_url("/admin/bitcaster/application/", "https://docs.example.com/")
        == "https://docs.example.com/adm-guide/app/"
    )


def test_help_url_empty_doc_site() -> None:
    assert resolve_help_url("/admin/bitcaster/application/", "") is None


def test_help_url_no_match() -> None:
    assert resolve_help_url("/", "https://docs.example.com") is None


def test_every_pattern_matches_something() -> None:
    assert HELP_LINKS
    for pattern in HELP_LINKS:
        assert re.compile(pattern)
