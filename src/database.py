"""SQLite database functions for CollectLog."""

import json
import sqlite3
from datetime import datetime


VALID_CONDITIONS = ("excellent", "good", "fair", "poor")


def get_connection(db_path):
    """Create SQLite connection with Row objects."""
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(connection):
    """Create database tables if they do not exist."""
    cursor = connection.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            collection_type TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            acquisition_date TEXT NOT NULL,
            price REAL,
            condition TEXT NOT NULL,
            tags TEXT,
            custom_fields_json TEXT,
            FOREIGN KEY (collection_id) REFERENCES collections(id)
                ON DELETE CASCADE
        )
        """
    )
    connection.commit()


def create_collection(connection, name, collection_type):
    """Create a new collection and return its id."""
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO collections (name, collection_type, created_at)
        VALUES (?, ?, ?)
        """,
        (name, collection_type, created_at),
    )
    connection.commit()
    return cursor.lastrowid


def get_collection(connection, collection_id):
    """Return one collection by id."""
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, name, collection_type, created_at
        FROM collections
        WHERE id = ?
        """,
        (collection_id,),
    )
    row = cursor.fetchone()
    return dict(row) if row else None


def list_collections(connection):
    """Return all collections."""
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id, name, collection_type, created_at
        FROM collections
        ORDER BY id
        """
    )
    return [dict(row) for row in cursor.fetchall()]


def delete_collection(connection, collection_id):
    """Delete collection and related items."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
    connection.commit()
    return cursor.rowcount


def create_item(
    connection,
    collection_id,
    title,
    description,
    acquisition_date,
    price,
    condition,
    tags,
    custom_fields,
):
    """Create a new item inside a collection."""
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO items (
            collection_id, title, description, acquisition_date, price,
            condition, tags, custom_fields_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            collection_id,
            title,
            description,
            acquisition_date,
            price,
            condition,
            ",".join(tags),
            json.dumps(custom_fields, ensure_ascii=False),
        ),
    )
    connection.commit()
    return cursor.lastrowid


def update_item(connection, item_id, item_data):
    """Update an item using a prepared dictionary."""
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE items
        SET title = ?, description = ?, acquisition_date = ?, price = ?,
            condition = ?, tags = ?, custom_fields_json = ?
        WHERE id = ?
        """,
        (
            item_data["title"],
            item_data["description"],
            item_data["acquisition_date"],
            item_data["price"],
            item_data["condition"],
            ",".join(item_data["tags"]),
            json.dumps(item_data["custom_fields"], ensure_ascii=False),
            item_id,
        ),
    )
    connection.commit()
    return cursor.rowcount


def delete_item(connection, item_id):
    """Delete one item by id."""
    cursor = connection.cursor()
    cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
    connection.commit()
    return cursor.rowcount


def get_item(connection, item_id):
    """Return one item by id."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    return row_to_item(row) if row else None


def list_items(connection, collection_id):
    """Return all items for a selected collection."""
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM items
        WHERE collection_id = ?
        ORDER BY id
        """,
        (collection_id,),
    )
    return [row_to_item(row) for row in cursor.fetchall()]


def search_items(connection, collection_id, query):
    """Search items by title or description."""
    like_query = f"%{query}%"
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT * FROM items
        WHERE collection_id = ?
          AND (title LIKE ? OR description LIKE ?)
        ORDER BY title
        """,
        (collection_id, like_query, like_query),
    )
    return [row_to_item(row) for row in cursor.fetchall()]


def row_to_item(row):
    """Convert SQLite row to ordinary dictionary."""
    custom_fields = {}
    tags = []

    if row["tags"]:
        tags = [tag.strip() for tag in row["tags"].split(",")]
        tags = [tag for tag in tags if tag]

    if row["custom_fields_json"]:
        try:
            custom_fields = json.loads(row["custom_fields_json"])
        except json.JSONDecodeError:
            custom_fields = {}

    return {
        "id": row["id"],
        "collection_id": row["collection_id"],
        "title": row["title"],
        "description": row["description"] or "",
        "acquisition_date": row["acquisition_date"],
        "price": row["price"],
        "condition": row["condition"],
        "tags": tags,
        "custom_fields": custom_fields,
    }
