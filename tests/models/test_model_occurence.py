from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bitcaster.models import Occurrence


def test_model_occurence(occurence: "Occurrence"):
    assert occurence.process()
