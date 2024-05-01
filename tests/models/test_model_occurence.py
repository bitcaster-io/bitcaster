from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Occurrence


def test_model_occurrence(occurrence: "Occurrence"):
    assert occurrence.process()


def test_str(occurrence: "Occurrence"):
    assert str(occurrence)
