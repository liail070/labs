from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Type, TypeVar
import json
import xml.etree.ElementTree as ET


class SocialNetworkError(Exception):
    """Базовое исключение для ошибок приложения."""


class ValidationError(SocialNetworkError):
    """Ошибка проверки корректности данных."""


class EntityNotFoundError(SocialNetworkError):
    """Ошибка: объект с указанным идентификатором не найден."""


class DuplicateEntityError(SocialNetworkError):
    """Ошибка: объект с таким идентификатором уже существует."""

@dataclass
class User:
    """Учётная запись пользователя социальной сети."""

    id: int
    username: str
    email: str
    password_hash: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validate(self) -> None:
        if not self.username.strip():
            raise ValidationError("Имя пользователя не должно быть пустым.")
        if "@" not in self.email or "." not in self.email.split("@")[-1]:
            raise ValidationError("Некорректный адрес электронной почты.")


@dataclass
class Profile:
    """Дополнительная информация о пользователе."""

    id: int
    user_id: int
    display_name: str
    bio: str = ""
    avatar_url: str = ""

    def validate(self) -> None:
        if not self.display_name.strip():
            raise ValidationError("Отображаемое имя профиля не должно быть пустым.")


@dataclass
class Post:
    """Публикация пользователя."""

    id: int
    author_id: int
    text: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validate(self) -> None:
        if not self.text.strip():
            raise ValidationError("Текст публикации не должен быть пустым.")


@dataclass
class Comment:
    """Комментарий к публикации."""

    id: int
    post_id: int
    author_id: int
    text: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validate(self) -> None:
        if not self.text.strip():
            raise ValidationError("Комментарий не должен быть пустым.")


@dataclass
class Like:
    """Отметка «Нравится» для публикации."""

    id: int
    post_id: int
    user_id: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Friendship:
    """Связь дружбы между двумя пользователями."""

    id: int
    user_id: int
    friend_id: int
    status: str = "pending"

    def validate(self) -> None:
        allowed = {"pending", "accepted", "blocked"}
        if self.status not in allowed:
            raise ValidationError(f"Недопустимый статус дружбы: {self.status}")


@dataclass
class Message:
    """Личное сообщение от одного пользователя другому."""

    id: int
    sender_id: int
    recipient_id: int
    text: str
    sent_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def validate(self) -> None:
        if not self.text.strip():
            raise ValidationError("Сообщение не должно быть пустым.")


@dataclass
class Conversation:
    """Диалог, в котором могут участвовать несколько пользователей."""

    id: int
    title: str
    participant_ids: List[int] = field(default_factory=list)


@dataclass
class Group:
    """Группа социальной сети."""

    id: int
    name: str
    description: str
    owner_id: int

    def validate(self) -> None:
        if not self.name.strip():
            raise ValidationError("Название группы не должно быть пустым.")


@dataclass
class GroupMembership:
    """Участие пользователя в группе."""

    id: int
    group_id: int
    user_id: int
    role: str = "member"


@dataclass
class Notification:
    """Уведомление для пользователя."""

    id: int
    user_id: int
    text: str
    is_read: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


@dataclass
class Media:
    """Медиафайл, принадлежащий пользователю."""

    id: int
    owner_id: int
    file_name: str
    media_type: str


@dataclass
class Hashtag:
    """Хэштег, который можно использовать в публикациях."""

    id: int
    name: str

    def validate(self) -> None:
        if not self.name.strip():
            raise ValidationError("Хэштег не должен быть пустым.")


@dataclass
class Feed:
    """Лента публикаций конкретного пользователя."""

    id: int
    user_id: int
    post_ids: List[int] = field(default_factory=list)


T = TypeVar("T")

class SocialNetwork:
    """Управляет сущностями социальной сети и хранением данных."""

    COLLECTIONS: Dict[str, Type[Any]] = {
        "users": User,
        "profiles": Profile,
        "posts": Post,
        "comments": Comment,
        "likes": Like,
        "friendships": Friendship,
        "messages": Message,
        "conversations": Conversation,
        "groups": Group,
        "memberships": GroupMembership,
        "notifications": Notification,
        "media": Media,
        "hashtags": Hashtag,
        "feeds": Feed,
    }

    def __init__(self) -> None:
        self.data: Dict[str, Dict[int, Any]] = {
            name: {} for name in self.COLLECTIONS
        }

    def create(self, collection: str, entity: T) -> T:
        """Добавляет новый объект в указанную коллекцию."""
        self._check_collection(collection)

        entity_id = getattr(entity, "id", None)
        if entity_id is None:
            raise ValidationError("У сущности должен быть идентификатор.")

        if entity_id in self.data[collection]:
            raise DuplicateEntityError(
                f"Объект с id={entity_id} уже существует в {collection}."
            )

        self._validate(entity)

        self.data[collection][entity_id] = entity
        return entity

    def get(self, collection: str, entity_id: int) -> T:
        """Возвращает объект по названию коллекции и его идентификатору."""
        self._check_collection(collection)
        try:
            return self.data[collection][entity_id]
        except KeyError as exc:
            raise EntityNotFoundError(
                f"Объект {collection} с id={entity_id} не найден."
            ) from exc

    def update(self, collection: str, entity_id: int, **changes: Any) -> T:
        """Изменяет указанные поля существующего объекта."""
        entity = self.get(collection, entity_id)

        for field_name, value in changes.items():
            if not hasattr(entity, field_name):
                raise ValidationError(
                    f"Поле {field_name!r} отсутствует у объекта."
                )
            setattr(entity, field_name, value)

        self._validate(entity)
        return entity

    def delete(self, collection: str, entity_id: int) -> None:
        """Удаляет объект из коллекции по идентификатору."""
        self._check_collection(collection)

        if entity_id not in self.data[collection]:
            raise EntityNotFoundError(
                f"Объект {collection} с id={entity_id} не найден."
            )

        del self.data[collection][entity_id]

    def list_all(self, collection: str) -> List[Any]:
        """Возвращает список всех объектов выбранной коллекции."""
        self._check_collection(collection)
        return list(self.data[collection].values())

    def save_json(self, path: str | Path) -> None:
        """Сохраняет все коллекции в JSON-файл."""
        payload = {
            name: [asdict(item) for item in entities.values()]
            for name, entities in self.data.items()
        }

        Path(path).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_json(self, path: str | Path) -> None:
        """Загружает данные из JSON-файла в объект социальной сети."""
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        self._load_records(payload)

    def save_xml(self, path: str | Path) -> None:
        """Сохраняет все коллекции в XML-файл."""
        root = ET.Element("social_network")

        for collection_name, entities in self.data.items():
            collection_node = ET.SubElement(root, collection_name)

            for entity in entities.values():
                entity_node = ET.SubElement(collection_node, "entity")

                for field_name, value in asdict(entity).items():
                    field_node = ET.SubElement(entity_node, field_name)

                    if isinstance(value, list):
                        for item in value:
                            ET.SubElement(field_node, "item").text = str(item)
                    else:
                        field_node.text = str(value)

        ET.indent(root, space="  ")
        ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)

    def load_xml(self, path: str | Path) -> None:
        """Загружает данные из XML-файла."""
        root = ET.parse(path).getroot()
        payload: Dict[str, List[Dict[str, Any]]] = {}

        for collection_node in root:
            if collection_node.tag not in self.COLLECTIONS:
                continue

            cls = self.COLLECTIONS[collection_node.tag]
            annotations = getattr(cls, "__annotations__", {})
            records: List[Dict[str, Any]] = []

            for entity_node in collection_node:
                record: Dict[str, Any] = {}

                for field_node in entity_node:
                    if field_node.tag not in annotations:
                        continue

                    if list(field_node):
                        value: Any = [item.text or "" for item in field_node]
                    else:
                        value = field_node.text or ""

                    record[field_node.tag] = self._convert_value(
                        annotations[field_node.tag], value
                    )

                records.append(record)

            payload[collection_node.tag] = records

        self._load_records(payload)


    def _load_records(self, payload: Dict[str, List[Dict[str, Any]]]) -> None:
        """Создаёт объекты из подготовленных записей JSON или XML."""
        self.data = {name: {} for name in self.COLLECTIONS}

        for collection_name, records in payload.items():
            if collection_name not in self.COLLECTIONS:
                continue

            cls = self.COLLECTIONS[collection_name]

            for record in records:
                self.create(collection_name, cls(**record))

    def _check_collection(self, collection: str) -> None:
        """Проверяет, существует ли коллекция с таким названием."""
        if collection not in self.COLLECTIONS:
            raise ValidationError(f"Неизвестная коллекция: {collection}")

    @staticmethod
    def _validate(entity: Any) -> None:
        """Вызывает метод validate у объекта, если такой метод есть."""
        validator = getattr(entity, "validate", None)
        if callable(validator):
            validator()

    @staticmethod
    def _convert_value(annotation: Any, value: Any) -> Any:
        """Преобразует строковые значения XML в нужные типы Python."""
        annotation_name = str(annotation)

        if "List[int]" in annotation_name or "list[int]" in annotation_name:
            return [int(item) for item in value]

        if annotation is int or annotation_name == "int":
            return int(value)
        if annotation is bool or annotation_name == "bool":
            return str(value).lower() == "true"

        return value


def create_demo_network() -> SocialNetwork:
    """Создаёт тестовую сеть с примерами пользователей и объектов."""
    network = SocialNetwork()

    network.create("users", User(1, "alice", "alice@example.com", "hash_alice"))
    network.create("users", User(2, "bob", "bob@example.com", "hash_bob"))
    network.create("profiles", Profile(1, 1, "Alice", "Разрабатываю учебные проекты на Python"))
    network.create("profiles", Profile(2, 2, "Bob", "Интересуюсь фото и технологиями"))

    network.create("posts", Post(1, 1, "Начинаю работу над новой лабораторной."))
    network.create("posts", Post(2, 2, "Сегодня разбираюсь с XML и JSON."))
    network.create("comments", Comment(1, 1, 2, "Удачи с лабораторной!"))

    network.create("likes", Like(1, 1, 2))
    network.create("friendships", Friendship(1, 1, 2, "accepted"))
    network.create("messages", Message(1, 1, 2, "Привет! Как продвигается проект?"))

    network.create("conversations", Conversation(1, "Обсуждение проекта", [1, 2]))
    network.create("groups", Group(1, "Python Lab", "Учебная группа по Python", 1))
    network.create("memberships", GroupMembership(1, 1, 2, "member"))

    network.create("notifications", Notification(1, 1, "Bob оценил вашу публикацию"))
    network.create("media", Media(1, 1, "project.png", "image"))
    network.create("hashtags", Hashtag(1, "python"))
    network.create("feeds", Feed(1, 1, [1, 2]))

    return network


def main() -> None:
    """Выполняет демонстрацию работы социальной сети."""
    base = Path(__file__).resolve().parent

    data_dir = base / "data"
    json_path = data_dir / "social_network.json"
    xml_path = data_dir / "social_network.xml"

    network = create_demo_network()

    network.update("posts", 1, text="Обновлённая публикация о лабораторной работе.")
    network.delete("likes", 1)
    network.create("likes", Like(2, 1, 2))

    network.save_json(json_path)
    network.save_xml(xml_path)

    restored = SocialNetwork()
    restored.load_json(json_path)

    print("JSON: пользователей =", len(restored.list_all("users")))
    print("JSON: публикаций =", len(restored.list_all("posts")))

    restored.load_xml(xml_path)
    print("XML: пользователей =", len(restored.list_all("users")))
    print("XML: публикаций =", len(restored.list_all("posts")))

    try:
        restored.get("users", 999)
    except EntityNotFoundError as exc:
        print("Обработано исключение:", exc)

    try:
        restored.create("users", User(1, "duplicate", "duplicate@example.com", "hash"))
    except DuplicateEntityError as exc:
        print("Обработано исключение:", exc)

    try:
        restored.create("posts", Post(99, 1, ""))
    except ValidationError as exc:
        print("Обработано исключение:", exc)


if __name__ == "__main__":
    main()
