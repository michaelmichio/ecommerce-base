"""
Advanced dynamic query utilities for SQLAlchemy.

Includes:
- Field-level filtering
- Full-text multi-field search
- Multi-column sorting
- Security validation (prevents unsafe fields/operators)

Generic version that works for any SQLAlchemy model.
"""

from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Query
from typing import List, Any, Sequence


# ----------------------------------------------------------------------
# 🛡️ Whitelist for safe operators
# ----------------------------------------------------------------------

SAFE_OPERATORS = {"eq", "like", "gt", "lt", "between"}


# ----------------------------------------------------------------------
# 🧹 Sanitization Helpers
# ----------------------------------------------------------------------

def sanitize_field(model, field: str):
    """
    Returns a SQLAlchemy Column if the field exists and is safe.
    Prevents SQL injection via invalid attribute names.
    """
    if not field or field.startswith("_"):
        return None

    return getattr(model, field, None)


def sanitize_value(value: Any):
    """
    Optional: normalize value types if needed.
    Currently left simple; can be expanded for date/string/UUID parsing.
    """
    return value


# ----------------------------------------------------------------------
# 🔍 FILTERING
# ----------------------------------------------------------------------

def apply_filters(query: Query, filters: Sequence, model) -> Query:
    """
    Apply field-level filtering based on dynamic filter objects.
    Each filter should include: { field, operator, value }

    Example:
        filters = [
            { "field": "price", "operator": "gt", "value": 100 },
            { "field": "category", "operator": "eq", "value": "Laptop" }
        ]
    """
    if not filters:
        return query

    for f in filters:
        # Validate field
        column = sanitize_field(model, getattr(f, "field", None))
        if not column:
            continue  # skip invalid fields safely

        # Validate operator
        op = getattr(f, "operator", "").lower()
        if op not in SAFE_OPERATORS:
            continue

        # Clean value
        val = sanitize_value(getattr(f, "value", None))

        # Apply filter
        if op == "eq":
            query = query.filter(column == val)

        elif op == "like":
            query = query.filter(column.ilike(f"%{val}%"))

        elif op == "gt":
            query = query.filter(column > val)

        elif op == "lt":
            query = query.filter(column < val)

        elif op == "between":
            if isinstance(val, (list, tuple)) and len(val) == 2:
                query = query.filter(column.between(val[0], val[1]))

    return query


# ----------------------------------------------------------------------
# 🔍 FULL-TEXT SEARCH
# ----------------------------------------------------------------------

def apply_search(query: Query, search, model) -> Query:
    """
    Apply multi-field search using `ilike`.
    search.value = string
    search.fields = ["name", "description"]
    """
    if not search or not search.value:
        return query

    value = search.value
    fields = search.fields or []

    conditions = []

    for field in fields:
        column = sanitize_field(model, field)
        if column is not None:
            # Only allow ilike on string-compatible columns
            try:
                conditions.append(column.ilike(f"%{value}%"))
            except Exception:
                pass  # skip non-string columns safely

    if conditions:
        query = query.filter(or_(*conditions))

    return query


# ----------------------------------------------------------------------
# 🔽 SORTING
# ----------------------------------------------------------------------

def apply_sort(query: Query, sort: Sequence, model) -> Query:
    """
    Apply multi-column sorting.
    Each sort item should include: { field, direction }
    direction = "asc" | "desc"
    """
    if not sort:
        return query  # let API specify default order

    clauses = []

    for s in sort:
        field = getattr(s, "field", None)
        direction = getattr(s, "direction", "asc")

        column = sanitize_field(model, field)
        if not column:
            continue

        if direction == "asc":
            clauses.append(asc(column))
        else:
            clauses.append(desc(column))

    if clauses:
        query = query.order_by(*clauses)

    return query
