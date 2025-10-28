from sqlalchemy import asc, desc, or_, and_
from sqlalchemy.orm import Query
from app.models.product import Product

def apply_filters(query: Query, filters):
    if not filters:
        return query

    for f in filters:
        column = getattr(Product, f.field, None)
        if not column:
            continue

        op = f.operator.lower()
        val = f.value

        if op == "eq":
            query = query.filter(column == val)
        elif op == "like":
            query = query.filter(column.ilike(f"%{val}%"))
        elif op == "gt":
            query = query.filter(column > val)
        elif op == "lt":
            query = query.filter(column < val)
        elif op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
            query = query.filter(column.between(val[0], val[1]))

    return query


def apply_search(query: Query, search):
    if not search or not search.value:
        return query

    value = search.value
    fields = search.fields or ["name", "description"]
    conditions = []

    for f in fields:
        column = getattr(Product, f, None)
        if column is not None:
            conditions.append(column.ilike(f"%{value}%"))

    if conditions:
        query = query.filter(or_(*conditions))

    return query


def apply_sort(query: Query, sort):
    if not sort:
        return query.order_by(desc(Product.created_at))

    order_clauses = []
    for s in sort:
        column = getattr(Product, s.field, None)
        if column is not None:
            order_clauses.append(asc(column) if s.direction == "asc" else desc(column))

    if order_clauses:
        query = query.order_by(*order_clauses)

    return query
