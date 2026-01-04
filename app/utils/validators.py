"""Validation utilities."""

import re


def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID.

    Args:
        uuid_string: String to validate

    Returns:
        True if valid UUID
    """
    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    return bool(uuid_pattern.match(uuid_string))


def is_valid_slug(slug: str) -> bool:
    """Check if string is a valid slug.

    Args:
        slug: String to validate

    Returns:
        True if valid slug
    """
    slug_pattern = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    return bool(slug_pattern.match(slug))

