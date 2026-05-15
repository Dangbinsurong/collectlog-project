"""Filtering, sorting and statistics functions."""

from collections import Counter


SORT_FIELDS = {
    "date": "acquisition_date",
    "title": "title",
    "price": "price",
}


def sort_items(items, sort_by):
    """Sort items by date, title or price using sorted with lambda."""
    field = SORT_FIELDS.get(sort_by, "title")

    if field == "price":
        return sorted(
            items,
            key=lambda item: item[field]
            if item[field] is not None else float("inf"),
        )

    return sorted(items, key=lambda item: item[field])


def filter_by_tag(items, tag):
    """Filter items by tag using filter and lambda."""
    return list(filter(lambda item: tag in item["tags"], items))


def filter_by_condition(items, condition):
    """Filter items by condition."""
    return list(filter(lambda item: item["condition"] == condition, items))


def create_custom_field_filter(key, value):
    """Return closure for filtering by custom field key and value."""
    return lambda item: str(item["custom_fields"].get(key)) == str(value)


def filter_by_custom_field(items, key, value):
    """Filter items with a closure created by factory function."""
    custom_filter = create_custom_field_filter(key, value)
    return list(filter(custom_filter, items))


def extract_prices(items):
    """Extract prices using map and lambda."""
    prices = list(map(lambda item: item["price"], items))
    return [price for price in prices if price is not None]


def calculate_total_price(items):
    """Calculate total price only for items where price is present."""
    return sum(extract_prices(items))


def calculate_average_price(items):
    """Calculate average price if at least one price is present."""
    prices = extract_prices(items)
    if not prices:
        return None
    return sum(prices) / len(prices)


def condition_distribution(items):
    """Return condition statistics as a dictionary."""
    total = len(items)
    counter = Counter(item["condition"] for item in items)
    result = {}

    for condition, count in counter.items():
        percent = 0 if total == 0 else count / total * 100
        result[condition] = {
            "count": count,
            "percent": percent,
            "bar": "█" * max(1, round(percent / 10)),
        }

    return result


def collection_summary(items):
    """Return summary data for one collection."""
    return {
        "total_items": len(items),
        "average_price": calculate_average_price(items),
        "total_price": calculate_total_price(items),
        "conditions": condition_distribution(items),
    }


def compare_collections(items_a, items_b, mode):
    """Compare two collections by count or total price."""
    if mode == "price":
        value_a = calculate_total_price(items_a)
        value_b = calculate_total_price(items_b)
    else:
        value_a = len(items_a)
        value_b = len(items_b)

    if value_a > value_b:
        winner = "first"
    elif value_b > value_a:
        winner = "second"
    else:
        winner = "equal"

    return {
        "mode": mode,
        "first": value_a,
        "second": value_b,
        "winner": winner,
    }
