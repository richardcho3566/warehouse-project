"""Utility helpers for the inventory app."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LocationCode:
    """Parsed warehouse location code.

    Supported examples:
    - B0F21    -> B / 0F / 2  / 1
    - B0F101   -> B / 0F / 10 / 1
    - B0F2     -> B / 0F / 2  / all levels
    - B-0F-21  -> B / 0F / 2  / 1
    - B/0F/2/1 -> B / 0F / 2 / 1
    - B/0F/2   -> B / 0F / 2 / all levels
    """

    warehouse: str
    shelf_number: str
    column: str = ""
    level: str = ""

    @property
    def is_exact(self) -> bool:
        return bool(self.warehouse and self.shelf_number and self.column and self.level)


def parse_location_code(raw_code: str | None) -> LocationCode | None:
    """Parse a human-readable or QR location code.

    Location rules used by the current warehouse app:
    - First character: warehouse, e.g. A/B
    - Next two characters: shelf number, e.g. 01/0F
    - Middle part: column, e.g. A/B/1/2/10
    - Last character: level/floor, e.g. 1/2/3/4

    If only warehouse+shelf are supplied, the caller can use it as a shelf-level
    search. If warehouse+shelf+column+level are supplied, the caller can do an
    exact location search.
    """

    if not raw_code:
        return None

    code = str(raw_code).strip().upper()
    if not code:
        return None

    # QR labels may use slash-separated values: A/01/B/3
    if "/" in code:
        parts = [part.strip() for part in code.split("/") if part.strip()]
        if len(parts) == 4:
            return LocationCode(
                warehouse=parts[0],
                shelf_number=parts[1],
                column=parts[2],
                level=parts[3],
            )
        if len(parts) == 3:
            return LocationCode(
                warehouse=parts[0],
                shelf_number=parts[1],
                column=parts[2],
            )
        if len(parts) == 2:
            return LocationCode(warehouse=parts[0], shelf_number=parts[1])
        return None

    compact = code.replace("-", "").replace(" ", "")

    # Minimum shelf-level code: warehouse 1 + shelf 2 = 3 chars. Example: B0F
    if len(compact) < 3:
        return None

    warehouse = compact[0]
    shelf_number = compact[1:3]
    rest = compact[3:]

    # Shelf-level search: B0F
    if not rest:
        return LocationCode(warehouse=warehouse, shelf_number=shelf_number)

    # Column-level search: B0F2 means B / 0F / 2열 전체.
    # This is useful when the user wants every level in the same column.
    if len(rest) == 1:
        return LocationCode(
            warehouse=warehouse,
            shelf_number=shelf_number,
            column=rest,
        )

    # Exact location search: last character is level, everything before it is column.
    # This supports numeric columns such as 2/10/13 and alphabetic columns such as A/B.
    column = rest[:-1]
    level = rest[-1]

    return LocationCode(
        warehouse=warehouse,
        shelf_number=shelf_number,
        column=column,
        level=level,
    )


def get_user_grade(user) -> str:
    """Return a safe grade string for templates and permission checks.

    Existing deployments may have users created before the Profile model was
    added. Accessing ``user.profile.grade`` directly can raise
    RelatedObjectDoesNotExist and cause a 500 page right after login. This
    helper creates the missing profile when possible and falls back to GRADE1
    instead of crashing if migrations have not run yet.
    """

    if not getattr(user, "is_authenticated", False):
        return ""

    try:
        from django.db.utils import OperationalError, ProgrammingError
        from .models import Profile

        profile, _ = Profile.objects.get_or_create(user=user, defaults={"grade": "GRADE1"})
        return profile.grade or "GRADE1"
    except (AttributeError, OperationalError, ProgrammingError):
        return "GRADE1"


def user_grade_context(request) -> dict:
    """Small context helper so templates never access user.profile directly."""

    return {"user_grade": get_user_grade(getattr(request, "user", None))}

