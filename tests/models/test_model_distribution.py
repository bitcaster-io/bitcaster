from typing import TYPE_CHECKING

import pytest
from testutils.factories import DistributionListFactory, EventFactory

from django.core.exceptions import ValidationError

if TYPE_CHECKING:
    from bitcaster.models import Application, DistributionList, Event

pytestmark = [pytest.mark.models, pytest.mark.django_db]


def test_clean_application_matches_project() -> None:
    event: "Event" = EventFactory()
    dl: DistributionList = DistributionListFactory.build(
        project=event.application.project, application=event.application
    )
    dl.clean()


def test_clean_application_mismatched_project_raises_error() -> None:
    event1: "Event" = EventFactory()
    event2: "Event" = EventFactory()
    dl: DistributionList = DistributionListFactory.build(
        project=event1.application.project, application=event2.application
    )
    with pytest.raises(ValidationError):
        dl.clean()


def test_clean_application_null_allowed() -> None:
    dl: DistributionList = DistributionListFactory.build(application=None)
    dl.clean()


def test_clean_application_same_project_succeeds() -> None:
    event: "Event" = EventFactory()
    app: "Application" = event.application
    dl: DistributionList = DistributionListFactory.build(project=app.project, application=app)
    dl.clean()
