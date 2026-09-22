"""
Shared atomic sequence number generation utility.

Prevents race conditions in reference number generation across all apps
by using PostgreSQL advisory locks within atomic transactions.
"""
import logging
import re

from django.db import connection, transaction

logger = logging.getLogger(__name__)


def next_sequence_number(model_class, prefix, field_name="reference_number", width=4):
    """
    Generate the next atomic sequence number for a given model and prefix.

    Uses PostgreSQL advisory locks (pg_advisory_xact_lock) to prevent
    concurrent requests from generating duplicate reference numbers.

    Args:
        model_class: The Django model class to query.
        prefix: The prefix to match (e.g., "EDIV/MAIL/2026").
        field_name: The model field to search and generate (default: "reference_number").
        width: Zero-padded width for the sequence number (default: 4).

    Returns:
        int: The next sequence number (e.g., 1, 2, 3, ...).

    Example:
        seq = next_sequence_number(IncomingMail, "EDIV/MAIL/2026", "mail_number")
        ref = f"EDIV/MAIL/2026/{seq:04d}"  # "EDIV/MAIL/2026/0001"
    """
    lock_key = hash(f"{prefix}/{field_name}") % (2**31)

    with transaction.atomic():
        # PostgreSQL advisory lock: blocks concurrent callers with same key
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_key])

        # Find the latest existing number matching this prefix
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


def next_cross_table_sequence(model_classes, prefix, field_name="reference_number", width=4):
    """
    Generate the next atomic sequence number by checking across multiple models.

    Useful when different models share the same prefix namespace
    (e.g., IncomingMail and OutgoingMail both using "EDIV/MAIL").

    Args:
        model_classes: List of Django model classes to check.
        prefix: The prefix to match.
        field_name: The model field to search (default: "reference_number").
        width: Zero-padded width for the sequence number (default: 4).

    Returns:
        int: The next sequence number.
    """
    lock_key = hash(f"{prefix}/cross_table/{field_name}") % (2**31)

    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_key])

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
