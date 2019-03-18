# -*- coding: utf-8 -*-
import logging
from uuid import uuid4

from django.utils.crypto import get_random_string
from django.utils.text import slugify

logger = logging.getLogger(__name__)


# credits: adapetd from Sentry `slugify_instance`

def slugify_instance(inst, label, reserved=(), max_length=30, *args, **kwargs):
    base_value = str(slugify(label)[:max_length]).strip()
    if base_value in reserved:
        base_value = None

    if not base_value:
        base_value = uuid4().hex[:12]

    base_qs = type(inst).objects.all()
    if inst.id:
        base_qs = base_qs.exclude(id=inst.id)
    if args or kwargs:
        base_qs = base_qs.filter(*args, **kwargs)

    inst.slug = base_value

    # We don't need to further mutate if we're unique at this point
    if not base_qs.filter(slug__iexact=base_value).exists():
        return

    # first we try with pk
    if inst.id:
        inst.slug = '%s%s' % (base_value, inst.id)
        if not base_qs.filter(slug__iexact=inst.slug).exists():
            return

    # We want to sanely generate the shortest unique slug possible, so
    # we try different length endings until we get one that works, or bail.

    # At most, we have 27 attempts here to derive a unique slug
    sizes = (
        (1, 2),  # (36^2) possibilities, 2 attempts
        (5, 3),  # (36^3) possibilities, 3 attempts
        (20, 5),  # (36^5) possibilities, 20 attempts
        (1, 12),  # (36^12) possibilities, 1 final attempt
    )
    for attempts, size in sizes:
        for i in range(attempts):
            end = get_random_string(size, allowed_chars='abcdefghijklmnopqrstuvwxyz0123456790')
            value = base_value[:max_length - size - 1] + '-' + end
            inst.slug = value
            if not base_qs.filter(slug__iexact=value).exists():
                return

    # If at this point, we've exhausted all possibilities, we'll just end up hitting
    # an IntegrityError from database, which is ok, and unlikely to happen
