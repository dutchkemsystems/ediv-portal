"""
Shared atomic sequence number generation utility.

Prevents race conditions in reference number generation across all apps
by using PostgreSQL advisory locks within atomic transactions.
"""

import logging
import re

from django.db import connection, transaction

logger = logging.getLogger(__name__)


def _advisory_lock(lock_key):
    """Acquire PostgreSQL advisory lock, skip on non-PostgreSQL backends."""
    vendor = connection.vendor
    if vendor == "postgresql":
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_key])
    # SQLite/others: no advisory lock support, rely on unique constraints


def next_sequence_number(model_class, prefix, field_name="reference_number", width=4):
    lock_key = hash(f"{prefix}/{field_name}") % (2**31)

    with transaction.atomic():
        _advisory_lock(lock_key)

        last_number = (
            model_class.objects.filter(**{f"{field_name}__startswith": prefix})
            .order_by(f"-{field_name}")
            .values_list(field_name, flat=True)
            .first()
        )

        seq = 1
        if last_number:
            match = re.search(rf"(\d{{{width}}})$", last_number)
            if match:
                seq = int(match.group(1)) + 1

    return seq


def next_cross_table_sequence(
    model_classes, prefix, field_name="reference_number", width=4
):
    lock_key = hash(f"{prefix}/cross_table/{field_name}") % (2**31)

    with transaction.atomic():
        _advisory_lock(lock_key)

        last_number = None
        for model_class in model_classes:
            existing = (
                model_class.objects.filter(**{f"{field_name}__startswith": prefix})
                .order_by(f"-{field_name}")
                .values_list(field_name, flat=True)
                .first()
            )
            if existing and (last_number is None or existing > last_number):
                last_number = existing

        seq = 1
        if last_number:
            match = re.search(rf"(\d{{{width}}})$", last_number)
            if match:
                seq = int(match.group(1)) + 1

    return seq
