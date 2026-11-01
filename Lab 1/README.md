# Лабораторная работа №1 — Социальная сеть

Вариант предметной области: **социальная сеть**.

## Структура проекта

```text
Lab1_social_network/
├── data/
│   ├── social_network.json
│   ├── social_network.xml
│   └── social_network_data.txt
├── docs/
│   └── TEST_RESULTS.txt
├── uml/
│   ├── social_network_classes.png
│   └── social_network_classes.svg
├── .gitignore
├── README.md
└── main.py
```

## Что реализовано

- объектная модель социальной сети на Python;
- 15 классов, включая сервис `SocialNetwork`;
- CRUD-операции для коллекций сущностей;
- пользовательские исключения `ValidationError`, `EntityNotFoundError` и `DuplicateEntityError`;
- проверка входных данных;
- сохранение и загрузка JSON;
- сохранение и загрузка XML;
- демонстрационные данные;
- UML-диаграмма классов в PNG и SVG.

## Запуск

Требуется Python 3.10+.

```bash
python main.py
```

После запуска программа создаёт/обновляет файлы в каталоге `data` и демонстрирует обработку нескольких исключений.

## Примечание

Отчёт `report.docx` в этот комплект пока не включён: он будет подготовлен отдельно.
