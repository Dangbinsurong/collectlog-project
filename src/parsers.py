"""Parsing and validation helpers for user input."""

import json
from datetime import datetime

from database import VALID_CONDITIONS


def parse_tags(raw_tags):
    """Parse comma-separated tags into a clean list."""
    tags = [tag.strip() for tag in raw_tags.split(",")]
    return [tag for tag in tags if tag]


def parse_price(raw_price):
    """Parse optional price value."""
    raw_price = raw_price.strip().replace(",", ".")
    if not raw_price:
        return None

    price = float(raw_price)
    if price < 0:
        message = (
            "Стоимость не может "
            "быть отрицательной."
        )
        raise ValueError(message)
    return price


def validate_date(raw_date):
    """Validate date in YYYY-MM-DD format."""
    datetime.strptime(raw_date, "%Y-%m-%d")
    return raw_date


def validate_condition(condition):
    """Validate item condition."""
    if condition not in VALID_CONDITIONS:
        allowed = ", ".join(VALID_CONDITIONS)
        message = (
            "Состояние должно быть одним "
            f"из: {allowed}."
        )
        raise ValueError(message)
    return condition


def parse_custom_fields(raw_fields):
    """
    Parse custom fields.

    Supported formats:
    1. JSON: {"автор": "Харуки Мураками", "год": 2002}
    2. key=value pairs: автор=Мураками, год=2002
    """
    raw_fields = raw_fields.strip()
    if not raw_fields:
        return {}

    if raw_fields.startswith("{"):
        parsed = json.loads(raw_fields)
        if not isinstance(parsed, dict):
            message = (
                "JSON должен быть объектом "
                "с парами ключ-значение."
            )
            raise ValueError(message)
        return parsed

    result = {}
    pairs = [pair.strip() for pair in raw_fields.split(",")]
    for pair in pairs:
        if not pair:
            continue
        if "=" not in pair:
            message = (
                "Используйте формат "
                "ключ=значение."
            )
            raise ValueError(message)
        key, value = pair.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            message = (
                "Ключ пользовательского поля "
                "не может быть пустым."
            )
            raise ValueError(message)
        result[key] = value

    return result


def prepare_item_data(
    title,
    description,
    acquisition_date,
    price,
    condition,
    tags,
    custom_fields,
):
    """Validate and prepare item dictionary for database saving."""
    if not title.strip():
        message = (
            "Название предмета не может "
            "быть пустым."
        )
        raise ValueError(message)

    return {
        "title": title.strip(),
        "description": description.strip(),
        "acquisition_date": validate_date(acquisition_date.strip()),
        "price": parse_price(price),
        "condition": validate_condition(condition.strip()),
        "tags": parse_tags(tags),
        "custom_fields": parse_custom_fields(custom_fields),
    }
