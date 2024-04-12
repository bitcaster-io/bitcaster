from itertools import zip_longest
from typing import Optional, Iterable


def grouper(iterable: Iterable[str], n: int, fillvalue: Optional[str] = None) -> str:
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC-DEF-Gxx"
    args = [iter(iterable)] * n
    ret: list[str] = []
    for x in zip_longest(*args, fillvalue=fillvalue):
        ret.append("".join(x))  # type: ignore
    return "-".join(ret)
