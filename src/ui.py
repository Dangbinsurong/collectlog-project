"""Console UI helper functions."""

from database import VALID_CONDITIONS


def print_title(text):
    """Print section title."""
    line = "=" * len(text)
    print(f"\n{line}\n{text}\n{line}")


def ask_text(prompt, required=True):
    """Ask user for text input."""
    while True:
        value = input(prompt).strip()
        if value or not required:
            return value
        print("Поле не может быть пустым.")


def ask_int(prompt):
    """Ask user for integer value."""
    while True:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Введите целое число.")


def choose_condition():
    """Ask user to choose valid item condition."""
    print("Состояние:", ", ".join(VALID_CONDITIONS))
    return ask_text("Введите состояние: ")


def show_collections(collections):
    """Print collections list."""
    if not collections:
        print("Коллекций пока нет.")
        return

    print("\nСписок коллекций:")
    for collection in collections:
        print(
            f"{collection['id']}. {collection['name']} "
            f"[{collection['collection_type']}] "
            f"создана: {collection['created_at']}"
        )


def show_items(items, currency):
    """Print items list."""
    if not items:
        print("Предметов не найдено.")
        return

    for item in items:
        price = "не указана"
        if item["price"] is not None:
            price = f"{item['price']:.2f} {currency}"

        tags = ", ".join(item["tags"]) if item["tags"] else "нет"
        custom_fields = item["custom_fields"] or {}

        print("-" * 60)
        print(f"ID: {item['id']}")
        print(f"Название: {item['title']}")
        print(f"Описание: {item['description']}")
        print(f"Дата приобретения: {item['acquisition_date']}")
        print(f"Стоимость: {price}")
        print(f"Состояние: {item['condition']}")
        print(f"Теги: {tags}")
        print(f"Пользовательские поля: {custom_fields}")


def show_summary(summary, currency):
    """Print collection summary."""
    print("Общее количество предметов: "
          f"{summary['total_items']}")

    if summary["average_price"] is None:
        print("Средняя стоимость: нет данных")
    else:
        print("Средняя стоимость: "
              f"{summary['average_price']:.2f} {currency}")

    print("Общая стоимость: "
          f"{summary['total_price']:.2f} {currency}")
    print("Распределение по состоянию:")

    if not summary["conditions"]:
        print("Нет данных")
        return

    for condition, data in summary["conditions"].items():
        print(
            f"{condition}: {data['bar']} "
            f"{data['percent']:.0f}% ({data['count']} шт.)"
        )


def show_compare_result(result, first_name, second_name, currency):
    """Print result of two collections comparison."""
    unit = "шт."
    if result["mode"] == "price":
        unit = currency

    print(f"{first_name}: {result['first']:.2f} {unit}")
    print(f"{second_name}: {result['second']:.2f} {unit}")

    if result["winner"] == "first":
        print("Больше значение у коллекции: "
              f"{first_name}")
    elif result["winner"] == "second":
        print("Больше значение у коллекции: "
              f"{second_name}")
    else:
        print("Коллекции равны по выбранному "
              "показателю.")
