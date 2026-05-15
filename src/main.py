"""CollectLog console application entry point."""

import json
import sys

from analytics import (
    collection_summary,
    compare_collections,
    filter_by_condition,
    filter_by_custom_field,
    filter_by_tag,
    sort_items,
)
from config import ensure_directories, get_config
from data_io import backup_database, export_to_zip, import_from_zip
from database import (
    create_collection,
    create_item,
    delete_collection,
    delete_item,
    get_collection,
    get_connection,
    get_item,
    init_db,
    list_collections,
    list_items,
    search_items,
    update_item,
)
from logging_config import setup_logging
from parsers import prepare_item_data
from ui import (
    ask_int,
    ask_text,
    choose_condition,
    print_title,
    show_collections,
    show_compare_result,
    show_items,
    show_summary,
)


CONFIG = get_config()
ensure_directories(CONFIG)
LOGGER = setup_logging(CONFIG["log_file"])


def create_collection_flow(connection):
    """Console flow for creating a collection."""
    try:
        print_title("Создание коллекции")
        name = ask_text("Название коллекции: ")
        prompt = (
            "Тип коллекции "
            "(Книги, Винил и т.д.): "
        )
        collection_type = ask_text(prompt)
        collection_id = create_collection(connection, name, collection_type)
        LOGGER.info("Created collection id=%s name=%s", collection_id, name)
        print(f"Коллекция создана. ID: {collection_id}")
    except Exception as error:
        LOGGER.exception("Collection creation error: %s", error)
        print(f"Ошибка создания коллекции: {error}")


def delete_collection_flow(connection):
    """Console flow for deleting a collection."""
    try:
        show_collections(list_collections(connection))
        prompt = "ID коллекции для удаления: "
        collection_id = ask_int(prompt)
        deleted = delete_collection(connection, collection_id)
        if deleted:
            LOGGER.info("Deleted collection id=%s", collection_id)
            print("Коллекция удалена.")
        else:
            print("Коллекция не найдена.")
    except Exception as error:
        LOGGER.exception("Collection deletion error: %s", error)
        print(f"Ошибка удаления коллекции: {error}")


def ask_item_data(existing_item=None):
    """Ask user for item data and return prepared dictionary."""
    if existing_item:
        print("Оставьте поле пустым,")
        print("чтобы сохранить старое значение.")

    old = existing_item or {}
    title = ask_with_default("Название: ", old.get("title", ""), True)
    description = ask_with_default(
        "Описание: ",
        old.get("description", ""),
        False,
    )
    acquisition_date = ask_with_default(
        "Дата приобретения (YYYY-MM-DD): ",
        old.get("acquisition_date", ""),
        True,
    )

    old_price = ""
    if old.get("price") is not None:
        old_price = str(old.get("price"))
    price_prompt = "Стоимость (можно пусто): "
    price = ask_with_default(price_prompt, old_price, False)

    if existing_item:
        print(f"Текущее состояние: {old.get('condition', '')}")
    condition = choose_condition_with_default(old.get("condition", ""))

    old_tags = ", ".join(old.get("tags", []))
    tags = ask_with_default(
        "Теги через запятую: ",
        old_tags,
        False,
    )

    old_custom = ""
    if old.get("custom_fields"):
        old_custom = json.dumps(old.get("custom_fields"), ensure_ascii=False)
    custom_fields = ask_with_default(
        "Поля JSON или ключ=значение: ",
        old_custom,
        False,
    )

    return prepare_item_data(
        title,
        description,
        acquisition_date,
        price,
        condition,
        tags,
        custom_fields,
    )


def ask_with_default(prompt, default, required):
    """Ask text value and keep default if user enters empty value."""
    value = input(prompt).strip()
    if value:
        return value
    if default != "":
        return default
    if required:
        return ask_text(prompt, required=True)
    return ""


def choose_condition_with_default(default):
    """Ask condition with possible default value."""
    if default:
        prompt = (
            "Введите состояние "
            "или Enter для старого: "
        )
        value = input(prompt).strip()
        return value if value else default
    return choose_condition()


def add_item_flow(connection, collection_id):
    """Console flow for adding an item."""
    try:
        print_title("Добавление предмета")
        item_data = ask_item_data()
        item_id = create_item(
            connection,
            collection_id,
            item_data["title"],
            item_data["description"],
            item_data["acquisition_date"],
            item_data["price"],
            item_data["condition"],
            item_data["tags"],
            item_data["custom_fields"],
        )
        LOGGER.info("Created item id=%s collection=%s", item_id, collection_id)
        print(f"Предмет добавлен. ID: {item_id}")
    except Exception as error:
        LOGGER.exception("Item creation error: %s", error)
        print(f"Ошибка добавления предмета: {error}")


def edit_item_flow(connection):
    """Console flow for editing an item."""
    try:
        prompt = "ID предмета для редактирования: "
        item_id = ask_int(prompt)
        existing_item = get_item(connection, item_id)
        if not existing_item:
            print("Предмет не найден.")
            return

        item_data = ask_item_data(existing_item)
        updated = update_item(connection, item_id, item_data)
        if updated:
            LOGGER.info("Updated item id=%s", item_id)
            print("Предмет обновлён.")
    except Exception as error:
        LOGGER.exception("Item update error: %s", error)
        print("Ошибка редактирования предмета: "
              f"{error}")


def delete_item_flow(connection):
    """Console flow for deleting an item."""
    try:
        item_id = ask_int("ID предмета для удаления: ")
        deleted = delete_item(connection, item_id)
        if deleted:
            LOGGER.info("Deleted item id=%s", item_id)
            print("Предмет удалён.")
        else:
            print("Предмет не найден.")
    except Exception as error:
        LOGGER.exception("Item deletion error: %s", error)
        print(f"Ошибка удаления предмета: {error}")


def view_items_flow(connection, collection_id):
    """View items with sorting."""
    try:
        print("Сортировка: date, title, price")
        sort_prompt = "Выберите сортировку: "
        sort_by = ask_text(sort_prompt, required=False)
        sort_by = sort_by if sort_by else "title"
        items = list_items(connection, collection_id)
        show_items(sort_items(items, sort_by), CONFIG["currency"])
    except Exception as error:
        LOGGER.exception("View items error: %s", error)
        print(f"Ошибка просмотра предметов: {error}")


def filter_items_flow(connection, collection_id):
    """Filter selected collection items."""
    try:
        print("1. По тегу")
        print("2. По состоянию")
        print("3. По пользовательскому полю")
        choice = ask_text("Выбор: ")
        items = list_items(connection, collection_id)

        if choice == "1":
            tag = ask_text("Введите тег: ")
            result = filter_by_tag(items, tag)
        elif choice == "2":
            condition = ask_text("Введите состояние: ")
            result = filter_by_condition(items, condition)
        elif choice == "3":
            key = ask_text("Ключ поля: ")
            value = ask_text("Значение поля: ")
            result = filter_by_custom_field(items, key, value)
        else:
            print("Нет такого пункта.")
            return

        show_items(result, CONFIG["currency"])
    except Exception as error:
        LOGGER.exception("Filter items error: %s", error)
        print(f"Ошибка фильтрации: {error}")


def search_items_flow(connection, collection_id):
    """Search items by title or description."""
    try:
        query = ask_text("Поисковый запрос: ")
        result = search_items(connection, collection_id, query)
        show_items(result, CONFIG["currency"])
    except Exception as error:
        LOGGER.exception("Search error: %s", error)
        print(f"Ошибка поиска: {error}")


def summary_flow(connection, collection_id):
    """Show collection summary."""
    try:
        items = list_items(connection, collection_id)
        summary = collection_summary(items)
        show_summary(summary, CONFIG["currency"])
    except Exception as error:
        LOGGER.exception("Summary error: %s", error)
        print(f"Ошибка сводки: {error}")


def export_flow(connection, collection_id=None):
    """Export one or all collections."""
    try:
        path = export_to_zip(
            connection,
            CONFIG["db_path"],
            CONFIG["export_dir"],
            collection_id,
        )
        LOGGER.info("Export created: %s", path)
        print(f"Экспорт создан: {path}")
    except Exception as error:
        LOGGER.exception("Export error: %s", error)
        print(f"Ошибка экспорта: {error}")


def import_flow(connection):
    """Import collections from ZIP archive."""
    try:
        path = ask_text("Путь к ZIP-архиву: ")
        count = import_from_zip(connection, path)
        LOGGER.info("Imported collections count=%s from=%s", count, path)
        print(f"Импортировано коллекций: {count}")
    except Exception as error:
        LOGGER.exception("Import error: %s", error)
        print(f"Ошибка импорта: {error}")


def backup_flow():
    """Create database backup."""
    try:
        path = backup_database(CONFIG["db_path"], CONFIG["backup_dir"])
        LOGGER.info("Backup created: %s", path)
        print(f"Резервная копия создана: {path}")
    except Exception as error:
        LOGGER.exception("Backup error: %s", error)
        print("Ошибка резервного копирования: "
              f"{error}")


def compare_flow(connection):
    """Compare two collections."""
    try:
        collections = list_collections(connection)
        show_collections(collections)
        first_id = ask_int("ID первой коллекции: ")
        second_id = ask_int("ID второй коллекции: ")
        print("Режим сравнения: count или price")
        mode = ask_text("Выбор: ")
        mode = "price" if mode == "price" else "count"

        first = get_collection(connection, first_id)
        second = get_collection(connection, second_id)
        if not first or not second:
            print("Одна из коллекций не найдена.")
            return

        result = compare_collections(
            list_items(connection, first_id),
            list_items(connection, second_id),
            mode,
        )
        show_compare_result(
            result,
            first["name"],
            second["name"],
            CONFIG["currency"],
        )
    except Exception as error:
        LOGGER.exception("Compare error: %s", error)
        print(f"Ошибка сравнения: {error}")


def collection_menu(connection, collection):
    """Menu for one selected collection."""
    while True:
        print_title(f"Коллекция: {collection['name']}")
        print("1. Просмотреть предметы")
        print("2. Добавить предмет")
        print("3. Редактировать предмет")
        print("4. Удалить предмет")
        print("5. Поиск")
        print("6. Фильтрация")
        print("7. Сводка")
        print("8. Экспорт этой коллекции")
        print("0. Назад")

        choice = ask_text("Выбор: ", required=False)
        if choice == "1":
            view_items_flow(connection, collection["id"])
        elif choice == "2":
            add_item_flow(connection, collection["id"])
        elif choice == "3":
            edit_item_flow(connection)
        elif choice == "4":
            delete_item_flow(connection)
        elif choice == "5":
            search_items_flow(connection, collection["id"])
        elif choice == "6":
            filter_items_flow(connection, collection["id"])
        elif choice == "7":
            summary_flow(connection, collection["id"])
        elif choice == "8":
            export_flow(connection, collection["id"])
        elif choice == "0":
            return
        else:
            print("Нет такого пункта.")


def select_collection_flow(connection):
    """Select collection and open collection menu."""
    try:
        collections = list_collections(connection)
        show_collections(collections)
        if not collections:
            return
        collection_id = ask_int("ID коллекции: ")
        collection = get_collection(connection, collection_id)
        if not collection:
            print("Коллекция не найдена.")
            return
        collection_menu(connection, collection)
    except Exception as error:
        LOGGER.exception("Select collection error: %s", error)
        print(f"Ошибка выбора коллекции: {error}")


def main_menu(connection):
    """Main application menu."""
    while True:
        title = (
            "CollectLog — персональный "
            "менеджер коллекций"
        )
        print_title(title)
        print("1. Список коллекций")
        print("2. Создать коллекцию")
        print("3. Открыть коллекцию")
        print("4. Удалить коллекцию")
        print("5. Сравнить две коллекции")
        print("6. Экспортировать все коллекции")
        print("7. Импортировать коллекции из ZIP")
        print("8. Создать резервную копию базы")
        print("0. Выход")

        choice = ask_text("Выбор: ", required=False)
        if choice == "1":
            show_collections(list_collections(connection))
        elif choice == "2":
            create_collection_flow(connection)
        elif choice == "3":
            select_collection_flow(connection)
        elif choice == "4":
            delete_collection_flow(connection)
        elif choice == "5":
            compare_flow(connection)
        elif choice == "6":
            export_flow(connection)
        elif choice == "7":
            import_flow(connection)
        elif choice == "8":
            backup_flow()
        elif choice == "0":
            print("До свидания!")
            break
        else:
            print("Нет такого пункта.")


def run():
    """Start application."""
    try:
        with get_connection(CONFIG["db_path"]) as connection:
            init_db(connection)
            LOGGER.info("Application started")
            main_menu(connection)
            LOGGER.info("Application finished")
    except KeyboardInterrupt:
        print("\nРабота остановлена "
              "пользователем.")
    except Exception as error:
        LOGGER.exception("Critical application error: %s", error)
        print(f"Критическая ошибка: {error}")
        sys.exit(1)


if __name__ == "__main__":
    run()
