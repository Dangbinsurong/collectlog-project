# CollectLog — персональный менеджер коллекций

CollectLog — консольное приложение на Python для учёта, каталогизации,
поиска, фильтрации, анализа, экспорта и импорта персональных коллекций:
книг, винила, растений, марок, монет, фигурок и других предметов.

Проект выполнен в процедурном и функциональном стиле. Пользовательские
классы и ООП не используются.

## Возможности проекта

- создание коллекций с указанием типа;
- добавление предметов внутри коллекции;
- хранение гибких пользовательских полей в JSON;
- теги для предметов;
- стоимость предмета как необязательное поле;
- сортировка по дате, названию и стоимости;
- фильтрация по тегу, состоянию и пользовательскому атрибуту;
- поиск по названию и описанию;
- сводка по коллекции:
  - общее количество предметов;
  - средняя стоимость;
  - общая стоимость;
  - распределение по состоянию в текстовом виде;
- сравнение двух коллекций по количеству или общей стоимости;
- хранение данных в SQLite;
- экспорт одной или всех коллекций в ZIP;
- импорт коллекций из ранее созданного ZIP-архива;
- резервное копирование базы данных в папку `backups/`;
- загрузка настроек из `.env` через `python-dotenv`;
- логирование событий в `app.log`;
- обработка ошибок через `try...except`.

## Структура проекта

```text
collectlog_project/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
└── src/
    ├── __init__.py
    ├── analytics.py
    ├── config.py
    ├── data_io.py
    ├── database.py
    ├── logging_config.py
    ├── main.py
    ├── parsers.py
    └── ui.py
```

После запуска автоматически создаются служебные папки:

```text
data/       # база данных SQLite
backups/    # резервные копии
exports/    # ZIP-экспорты
```

## Таблицы базы данных

Проект использует SQLite и создаёт таблицы автоматически.

### collections

```text
id INTEGER PRIMARY KEY AUTOINCREMENT
name TEXT NOT NULL
collection_type TEXT NOT NULL
created_at TEXT NOT NULL
```

В ТЗ указаны поля `id`, `name`, `created_at`. Поле
`collection_type` добавлено дополнительно, потому что в задании также
требуется создавать коллекцию с указанием её типа.

### items

```text
id INTEGER PRIMARY KEY AUTOINCREMENT
collection_id INTEGER NOT NULL
title TEXT NOT NULL
description TEXT
acquisition_date TEXT NOT NULL
price REAL
condition TEXT NOT NULL
tags TEXT
custom_fields_json TEXT
```

## Установка и запуск

1. Установите Python 3.10 или новее.

2. Откройте папку проекта в терминале.

3. Создайте виртуальное окружение:

```bash
python -m venv venv
```

4. Активируйте виртуальное окружение.

Windows:

```bash
venv\Scripts\activate
```

macOS / Linux:

```bash
source venv/bin/activate
```

5. Установите зависимости:

```bash
pip install -r requirements.txt
```

6. Создайте файл `.env` на основе `.env.example`:

```bash
copy .env.example .env
```

Для macOS / Linux:

```bash
cp .env.example .env
```

7. Запустите приложение:

```bash
python src/main.py
```

## Пример `.env`

```env
DB_PATH=data/collectlog.sqlite
DEFAULT_CURRENCY=RUB
BACKUP_DIR=backups
EXPORT_DIR=exports
LOG_FILE=app.log
```

## Пример пользовательских полей

При добавлении предмета можно вводить дополнительные поля двумя способами.

### Вариант 1: JSON

```json
{"автор": "Харуки Мураками", "год издания": 2002}
```

### Вариант 2: пары ключ=значение

```text
автор=Харуки Мураками, год издания=2002
```

## Пример тегов

```text
редкий, подарок, из Японии
```

## Пример состояний предмета

```text
excellent
good
fair
poor
```

## Где используются функциональные конструкции

### `filter` и `lambda`

Файл `src/analytics.py`:

```python
def filter_by_tag(items, tag):
    return list(filter(lambda item: tag in item["tags"], items))
```

### `map`

```python
def extract_prices(items):
    prices = list(map(lambda item: item["price"], items))
    return [price for price in prices if price is not None]
```

### `sorted` с `lambda`

```python
def sort_items(items, field):
    return sorted(items, key=lambda item: item[field])
```

### Замыкание

```python
def create_custom_field_filter(key, value):
    return lambda item: str(item["custom_fields"].get(key)) == str(value)
```

## Экспорт и импорт

Экспорт создаёт ZIP-архив в папке `exports/`. Архив содержит:

- `collections.json` — полные данные коллекции или всех коллекций;
- `database_backup.sqlite` — резервную копию базы данных.

Импорт читает `collections.json` из ZIP-архива и создаёт коллекции заново
с сохранением предметов, тегов и пользовательских полей.

## Резервное копирование

Пункт меню `Создать резервную копию базы` создаёт файл вида:

```text
backups/backup_20251028_0900.sqlite
```

## Git Workflow для сдачи проекта

Рекомендуемая последовательность:

```bash
git init
git add README.md .gitignore requirements.txt .env.example src/
git commit -m "Initial project structure"
```

Создание ветки для управления коллекциями:

```bash
git checkout -b feature/collection-manager
git add src/
git commit -m "Add collection and item management"
git push -u origin feature/collection-manager
```

Создание ветки для пользовательских полей:

```bash
git checkout main
git checkout -b feature/custom-fields
git add src/
git commit -m "Add custom fields parsing and filtering"
git push -u origin feature/custom-fields
```

Создание ветки для экспорта и импорта:

```bash
git checkout main
git checkout -b feature/export-import
git add src/
git commit -m "Add export import and backup features"
git push -u origin feature/export-import
```

После отправки веток на GitHub нужно создать минимум три Pull Request:

1. `feature/collection-manager` → `main`;
2. `feature/custom-fields` → `main`;
3. `feature/export-import` → `main`.

В каждом Pull Request нужно написать, что было реализовано, затем выполнить
самопроверку и нажать `Squash and Merge`.

## Защита ветки main на GitHub

В репозитории откройте:

```text
Settings → Branches → Branch protection rules → Add rule
```

Настройки:

- Branch name pattern: `main`;
- включить запрет прямых коммитов;
- включить обязательную работу через Pull Request;
- сохранить правило.

## Проверка соответствия ТЗ

| Требование | Реализация |
|---|---|
| Процедурный и функциональный стиль | Все модули состоят из функций, классы не используются |
| SQLite | `src/database.py` |
| JSON-поле | `custom_fields_json` |
| ZIP-экспорт | `src/data_io.py` |
| ZIP-импорт | `src/data_io.py` |
| Backup | `backup_database()` |
| `.env` и `python-dotenv` | `src/config.py` |
| Логирование | `src/logging_config.py` |
| Исключения | Все пользовательские операции обёрнуты в `try...except` |
| `filter`, `map`, `sorted`, `lambda` | `src/analytics.py` |
| Замыкание | `create_custom_field_filter()` |
| pathlib | `src/config.py`, `src/data_io.py` |
| PEP 8 | Код разбит на модули, имена в `snake_case` |

## Быстрый запуск на Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python src/main.py
```

После запуска пользователь может создать коллекцию, добавить предметы,
посмотреть сводку, выполнить экспорт в ZIP и создать резервную копию базы.

## Дополнительная проверка пользовательских полей

Пользовательские поля позволяют хранить разные характеристики предметов
в зависимости от типа коллекции.

Примеры для книг:

```text
автор=Харуки Мураками, год издания=2002, жанр=роман

исполнитель=Michael Jackson, год выпуска=1982, жанр=поп

тип=суккулент, высота=15 см, место=подоконник