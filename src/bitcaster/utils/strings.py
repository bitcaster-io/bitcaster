import random
import string


def truncatechars(value: str, length: int, ellipsis='...'):
    if len(value) > length:
        return value[:max(0, length - len(ellipsis))] + ellipsis
    return value


def random_string(length: int, elements: str = string.ascii_letters):
    return ''.join(random.choice(elements) for x in range(length))
