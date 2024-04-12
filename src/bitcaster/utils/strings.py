from itertools import zip_longest
from typing import Iterable, Optional


def grouper(iterable: Iterable[str], n: int, fillvalue: Optional[str] = None) -> str:
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return str(zip_longest(*args, fillvalue=fillvalue))
