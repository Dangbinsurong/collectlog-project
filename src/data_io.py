"""Export, import and backup functions for CollectLog."""

import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from database import (
    create_collection,
    create_item,
    list_collections,
    list_items,
)


def make_timestamp():
    """Return timestamp for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M")


def backup_database(db_path, backup_dir):
    """Create automatic SQLite database backup."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_path = backup_dir / f"backup_{make_timestamp()}.sqlite"

    if not db_path.exists():
        message = "База данных ещё не создана."
        raise FileNotFoundError(message)

    shutil.copy2(db_path, backup_path)
    return backup_path


def build_export_data(connection, collection_id=None):
    """Build full export data for one or all collections."""
    collections = list_collections(connection)
    if collection_id is not None:
        collections = [
            collection for collection in collections
            if collection["id"] == collection_id
        ]

    data = {
        "app": "CollectLog",
        "version": "1.0",
        "exported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "collections": [],
    }

    for collection in collections:
        items = list_items(connection, collection["id"])
        data["collections"].append(
            {
                "id": collection["id"],
                "name": collection["name"],
                "collection_type": collection["collection_type"],
                "created_at": collection["created_at"],
                "items": items,
            }
        )

    return data


def export_to_zip(connection, db_path, export_dir, collection_id=None):
    """Export one or all collections into ZIP archive."""
    export_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"collection_{collection_id}" if collection_id else "all"
    zip_path = export_dir / f"collectlog_{suffix}_{make_timestamp()}.zip"
    data = build_export_data(connection, collection_id)

    if not data["collections"]:
        raise ValueError("Нет коллекций для экспорта.")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "collections.json",
            json.dumps(data, ensure_ascii=False, indent=2),
        )
        if db_path.exists():
            archive.write(db_path, arcname="database_backup.sqlite")

    return zip_path


def read_export_json(zip_path):
    """Read collections.json from exported ZIP archive."""
    zip_path = Path(zip_path)
    if not zip_path.exists():
        raise FileNotFoundError("ZIP-архив не найден.")

    with zipfile.ZipFile(zip_path, "r") as archive:
        if "collections.json" not in archive.namelist():
            message = "В архиве нет файла collections.json."
            raise ValueError(message)
        with archive.open("collections.json") as json_file:
            return json.loads(json_file.read().decode("utf-8"))


def import_from_zip(connection, zip_path):
    """Import collections and items from exported ZIP archive."""
    data = read_export_json(zip_path)
    collections = data.get("collections", [])
    imported_count = 0

    if not collections:
        message = (
            "В архиве нет коллекций "
            "для импорта."
        )
        raise ValueError(message)

    for collection in collections:
        new_collection_id = create_collection(
            connection,
            collection.get("name", "Imported collection"),
            collection.get("collection_type", "Unknown"),
        )

        for item in collection.get("items", []):
            create_item(
                connection,
                new_collection_id,
                item.get("title", "Без названия"),
                item.get("description", ""),
                item.get("acquisition_date", "2000-01-01"),
                item.get("price"),
                item.get("condition", "good"),
                item.get("tags", []),
                item.get("custom_fields", {}),
            )

        imported_count += 1

    return imported_count
