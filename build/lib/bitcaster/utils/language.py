from typing import Callable, TypeVar

PropReturn = TypeVar("PropReturn")


def class_property(meth: Callable[..., PropReturn]) -> PropReturn:
    return classmethod(property(meth))  # type: ignore
